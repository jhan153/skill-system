"""Kanboard JSON-RPC adapter.

Write access to Kanboard goes through the JSON-RPC API only — never SQLite.
The transport is injectable: tests pass a fake callable so the adapter can be
exercised without a running Kanboard. The default transport uses urllib with
HTTP Basic auth (``username``:``token``) per Kanboard's API contract.

This adapter is an internal implementation detail. The MCP facade never
exposes raw methods like ``createTask`` — only plan-centric tools.
"""

from __future__ import annotations

import base64
import json
import urllib.request
from typing import Any, Callable, Optional

Transport = Callable[[dict], dict]


class KanboardError(RuntimeError):
    """Raised when the Kanboard JSON-RPC endpoint returns an error object."""


class KanboardClient:
    def __init__(
        self,
        url: str,
        username: str = "jsonrpc",
        token: Optional[str] = None,
        transport: Optional[Transport] = None,
        timeout: float = 10.0,
    ) -> None:
        self.url = url
        self.username = username
        self._token = token
        self._timeout = timeout
        self._transport = transport or self._http_transport
        self._id = 0

    # --- JSON-RPC core -----------------------------------------------------
    def call(self, method: str, **params: Any) -> Any:
        self._id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._id,
            "method": method,
            "params": params,
        }
        response = self._transport(payload)
        if isinstance(response, dict) and response.get("error"):
            raise KanboardError(f"{method}: {response['error']}")
        if isinstance(response, dict):
            return response.get("result")
        return response

    def _http_transport(self, payload: dict) -> dict:
        if not self._token:
            raise KanboardError(
                "no API token; set kanboard.token_env or configure kanboard.local_db_path"
            )
        data = json.dumps(payload).encode("utf-8")
        creds = base64.b64encode(
            f"{self.username}:{self._token}".encode("utf-8")
        ).decode("ascii")
        request = urllib.request.Request(
            self.url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {creds}",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self._timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # --- plan-centric convenience wrappers (internal use only) -------------
    def get_project_by_name(self, name: str) -> Any:
        return self.call("getProjectByName", name=name)

    def create_project(self, name: str, description: str = "") -> Any:
        return self.call("createProject", name=name, description=description)

    def get_columns(self, project_id: int) -> Any:
        return self.call("getColumns", project_id=project_id)

    def add_column(self, project_id: int, title: str) -> Any:
        return self.call("addColumn", project_id=project_id, title=title)

    def get_task_by_reference(self, project_id: int, reference: str) -> Any:
        return self.call(
            "getTaskByReference", project_id=project_id, reference=reference
        )

    def get_project_by_id(self, project_id: int) -> Any:
        return self.call("getProjectById", project_id=project_id)

    def get_user_by_name(self, username: str) -> Any:
        return self.call("getUserByName", username=username)

    def get_project_users(self, project_id: int) -> Any:
        return self.call("getProjectUsers", project_id=project_id)

    def add_project_user(
        self, project_id: int, user_id: int, role: str = "project-manager"
    ) -> Any:
        return self.call(
            "addProjectUser", project_id=project_id, user_id=user_id, role=role
        )

    def create_task(
        self,
        project_id: int,
        title: str,
        reference: str,
        column_id: Optional[int] = None,
        swimlane_id: Optional[int] = None,
        owner_id: Optional[int] = None,
        description: Optional[str] = None,
        color_id: Optional[str] = None,
        tags: Optional[list] = None,
    ) -> Any:
        params: dict[str, Any] = {
            "project_id": project_id,
            "title": title,
            "reference": reference,
        }
        if column_id is not None:
            params["column_id"] = column_id
        if swimlane_id is not None:
            params["swimlane_id"] = swimlane_id
        if owner_id is not None:
            params["owner_id"] = owner_id
        if description is not None:
            params["description"] = description
        if color_id is not None:
            params["color_id"] = color_id
        if tags:
            params["tags"] = tags
        return self.call("createTask", **params)

    def update_task(self, task_id: int, **fields: Any) -> Any:
        return self.call("updateTask", id=task_id, **fields)

    def get_all_tasks(self, project_id: int, status_id: int = 1) -> Any:
        return self.call("getAllTasks", project_id=project_id, status_id=status_id)

    def get_swimlanes(self, project_id: int) -> Any:
        return self.call("getActiveSwimlanes", project_id=project_id)

    def create_swimlane(self, project_id: int, name: str) -> Any:
        return self.call("addSwimlane", project_id=project_id, name=name)

    def create_subtask(self, task_id: int, title: str, status: int = 0) -> Any:
        return self.call("createSubtask", task_id=task_id, title=title, status=status)

    def move_task_position(
        self,
        project_id: int,
        task_id: int,
        column_id: int,
        position: int = 1,
        swimlane_id: int = 0,
    ) -> Any:
        return self.call(
            "moveTaskPosition",
            project_id=project_id,
            task_id=task_id,
            column_id=column_id,
            position=position,
            swimlane_id=swimlane_id,
        )

    def create_comment(self, task_id: int, content: str, user_id: int = 1) -> Any:
        return self.call(
            "createComment", task_id=task_id, user_id=user_id, content=content
        )
