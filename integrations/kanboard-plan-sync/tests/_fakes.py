"""In-memory Kanboard double for integration tests (no network).

Models just enough of the JSON-RPC surface used by the sync/snapshot/validation
paths. A freshly created project gets Kanboard-like default columns, so the
``ensure_columns`` add-column path is genuinely exercised.
"""

from __future__ import annotations

_KANBOARD_DEFAULT_COLUMNS = ["Backlog", "Ready", "Work in progress", "Done"]


class FakeKanboard:
    def __init__(self):
        self.projects: dict[int, dict] = {}
        self.columns: dict[int, dict[int, str]] = {}
        self.tasks: dict[int, dict] = {}
        self.comments: list[dict] = []
        self.subtasks: list[dict] = []
        self.users: dict[int, str] = {1: "admin"}  # preloaded admin like a fresh Kanboard
        self.project_users: dict[int, dict[int, str]] = {}
        self.swimlanes: dict[int, dict[int, str]] = {}  # project_id -> {swimlane_id: name}
        self._pid = 0
        self._tid = 0
        self._cid = 0
        self._sid = 0
        self._colid = 0
        self._swid = 0

    # --- users / members ---
    def get_user_by_name(self, username):
        for uid, name in self.users.items():
            if name == username:
                return {"id": uid, "username": name}
        return None

    def get_project_users(self, project_id):
        return dict(self.project_users.get(project_id, {}))

    def add_project_user(self, project_id, user_id, role="project-manager"):
        self.project_users.setdefault(project_id, {})[user_id] = self.users.get(
            user_id, str(user_id)
        )
        return True

    # --- projects / columns ---
    def get_project_by_name(self, name):
        for pid, p in self.projects.items():
            if p["name"] == name:
                return {"id": pid, "name": name}
        return None

    def create_project(self, name, description=""):
        self._pid += 1
        pid = self._pid
        self.projects[pid] = {"name": name, "description": description}
        self.columns[pid] = {}
        for title in _KANBOARD_DEFAULT_COLUMNS:
            self._colid += 1
            self.columns[pid][self._colid] = title
        self._swid += 1
        self.swimlanes[pid] = {self._swid: "Default"}  # fresh project default swimlane
        return pid

    # --- swimlanes ---
    def get_swimlanes(self, project_id):
        return [
            {"id": sid, "name": name}
            for sid, name in self.swimlanes.get(project_id, {}).items()
        ]

    def create_swimlane(self, project_id, name):
        self._swid += 1
        self.swimlanes.setdefault(project_id, {})[self._swid] = name
        return self._swid

    def get_columns(self, project_id):
        return [
            {"id": cid, "title": title}
            for cid, title in self.columns.get(project_id, {}).items()
        ]

    def add_column(self, project_id, title):
        self._colid += 1
        self.columns.setdefault(project_id, {})[self._colid] = title
        return self._colid

    # --- tasks ---
    def create_task(
        self,
        project_id,
        title,
        reference,
        column_id=None,
        swimlane_id=None,
        owner_id=None,
        description=None,
        color_id=None,
        tags=None,
    ):
        self._tid += 1
        tid = self._tid
        self.tasks[tid] = {
            "id": tid,
            "project_id": project_id,
            "title": title,
            "reference": reference,
            "column_id": column_id,
            "swimlane_id": swimlane_id,
            "owner_id": owner_id,
            "description": description,
            "color_id": color_id,
            "tags": tags,
        }
        return tid

    def update_task(self, task_id, **fields):
        self.tasks[task_id].update(fields)
        return True

    def move_task_position(self, project_id, task_id, column_id, position=1, swimlane_id=0):
        self.tasks[task_id]["column_id"] = column_id
        return True

    def get_all_tasks(self, project_id, status_id=1):
        return [t for t in self.tasks.values() if t["project_id"] == project_id]

    def get_task_by_reference(self, project_id, reference):
        for t in self.tasks.values():
            if t["project_id"] == project_id and t["reference"] == reference:
                return t
        return None

    # --- evidence ---
    def create_comment(self, task_id, content, user_id=1):
        self._cid += 1
        self.comments.append({"id": self._cid, "task_id": task_id, "content": content})
        return self._cid

    def create_subtask(self, task_id, title, status=0):
        self._sid += 1
        self.subtasks.append(
            {"id": self._sid, "task_id": task_id, "title": title, "status": status}
        )
        return self._sid
