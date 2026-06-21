import sqlite3
import tempfile
import unittest
from pathlib import Path

from kanboard_plan_sync.config import (
    DEFAULT_LOCAL_DB_PATH,
    KanboardConn,
    load_config,
    parse_config,
    resolve_token,
    resolve_token_info,
)
from kanboard_plan_sync.state import SyncState, TaskState, load_state, save_state

CONFIG_YAML = """
workspace:
  name: my-ws
kanboard:
  url: http://localhost:9/jsonrpc.php
  username: jsonrpc
  token_env: MY_TOKEN_VAR
  local_db_path: /tmp/kanboard-test.sqlite
plans:
  - path: docs/plan/p.md
    plan_type: long-term
    parent_plan_id: root
    kanboard_project_strategy: ops-swimlane
plan_discovery:
  glob:
    - docs/plan/*.md
"""


def write_kanboard_settings_db(path: Path, token: str) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute("create table settings (option text primary key, value text)")
        conn.execute(
            "insert into settings (option, value) values (?, ?)",
            ("api_token", token),
        )
        conn.commit()
    finally:
        conn.close()


class ConfigTest(unittest.TestCase):
    def test_load_config(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".kanboard-plan.yml").write_text(CONFIG_YAML, encoding="utf-8")
            cfg = load_config(d)
            self.assertEqual(cfg.name, "my-ws")
            self.assertEqual(cfg.kanboard.url, "http://localhost:9/jsonrpc.php")
            self.assertEqual(cfg.kanboard.token_env, "MY_TOKEN_VAR")
            self.assertEqual(cfg.kanboard.local_db_path, "/tmp/kanboard-test.sqlite")
            self.assertEqual(len(cfg.plans), 1)
            self.assertEqual(cfg.plans[0].plan_type, "long-term")
            entry = cfg.plan_entry_for("/somewhere/docs/plan/p.md")
            self.assertIsNotNone(entry)
            self.assertEqual(entry.parent_plan_id, "root")

    def test_missing_config_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                load_config(d)

    def test_defaults_when_keys_missing(self):
        cfg = parse_config({}, workspace_root="/ws", config_path="x")
        self.assertEqual(cfg.kanboard.username, "jsonrpc")
        self.assertEqual(cfg.kanboard.token_env, "KANBOARD_API_TOKEN")
        self.assertEqual(cfg.kanboard.local_db_path, DEFAULT_LOCAL_DB_PATH)
        self.assertEqual(cfg.plans, [])
        self.assertEqual(cfg.plan_discovery_globs, ["docs/plan/*.md"])

    def test_token_env_wins_over_local_db(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "db.sqlite"
            write_kanboard_settings_db(db, "db-secret")
            conn = KanboardConn(token_env="MY_TOKEN_VAR", local_db_path=str(db))
            info = resolve_token_info(conn, environ={"MY_TOKEN_VAR": "env-secret"})
            self.assertEqual(info.token, "env-secret")
            self.assertEqual(info.source, "env")
            self.assertEqual(resolve_token(conn, environ={"MY_TOKEN_VAR": "env-secret"}), "env-secret")

    def test_token_resolved_from_local_db_for_jsonrpc(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "db.sqlite"
            write_kanboard_settings_db(db, "db-secret")
            conn = KanboardConn(token_env="MY_TOKEN_VAR", local_db_path=str(db))
            info = resolve_token_info(conn, environ={})
            self.assertEqual(info.token, "db-secret")
            self.assertEqual(info.source, "local_db")

    def test_local_db_not_used_for_user_token_auth(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "db.sqlite"
            write_kanboard_settings_db(db, "db-secret")
            conn = KanboardConn(
                username="admin", token_env="MY_TOKEN_VAR", local_db_path=str(db)
            )
            info = resolve_token_info(conn, environ={})
            self.assertIsNone(info.token)
            self.assertEqual(info.source, "none")

    def test_missing_token_source_returns_none(self):
        conn = KanboardConn(token_env="MY_TOKEN_VAR", local_db_path="/no/such/db.sqlite")
        info = resolve_token_info(conn, environ={})
        self.assertIsNone(info.token)
        self.assertEqual(info.source, "none")


class StateTest(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            state = SyncState()
            state.upsert(
                "plan:A1",
                TaskState(
                    kanboard_task_id=12,
                    kanboard_project_id=3,
                    last_markdown_status="todo",
                    last_synced_column="TODO",
                ),
            )
            path = save_state(d, state)
            self.assertTrue(path.is_file())
            loaded = load_state(d)
            self.assertEqual(len(loaded.references), 1)
            ts = loaded.get("plan:A1")
            self.assertEqual(ts.kanboard_task_id, 12)
            self.assertEqual(ts.last_synced_column, "TODO")

    def test_missing_state_is_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(load_state(d).references, {})


if __name__ == "__main__":
    unittest.main()
