"""Command-line interface for kanboard-plan-sync core.

All commands are read-only / dry-run. Applying changes to a live Kanboard is
done through the MCP facade (or a future ``sync --apply``) and is intentionally
not wired here so the core stays verifiable offline.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from . import __version__, registry
from .bootstrap import init_workspace
from .config import load_config
from .rollout import sync_all
from .diff import build_diff, summarize_diff
from .manifest import build_manifest
from .token_guard import scan_workspace
from .state import load_state
from .workspace import inspect_workspace


def _emit(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _load_config_opt(workspace: Optional[str]):
    if not workspace:
        return None
    try:
        return load_config(workspace)
    except FileNotFoundError:
        return None


def cmd_inspect_workspace(args: argparse.Namespace) -> int:
    _emit(inspect_workspace(args.workspace))
    return 0


def cmd_build_manifest(args: argparse.Namespace) -> int:
    config = _load_config_opt(args.workspace)
    manifest = build_manifest(args.plan_path, config=config)
    _emit(manifest.to_dict())
    return 0


def cmd_check_secrets(args: argparse.Namespace) -> int:
    report = scan_workspace(args.workspace)
    _emit(report)
    return 0 if report["ok"] else 1


def cmd_diff(args: argparse.Namespace) -> int:
    config = _load_config_opt(args.workspace)
    manifest = build_manifest(args.plan_path, config=config)
    state = load_state(args.workspace) if args.workspace else load_state(".")
    ops = build_diff(manifest, state)
    _emit(
        {
            "plan_id": manifest.plan_id,
            "mode": "dry-run",
            "summary": summarize_diff(ops),
            "operations": [op.to_dict() for op in ops],
        }
    )
    return 0


def cmd_init_workspace(args: argparse.Namespace) -> int:
    report = init_workspace(args.workspace, force=args.force)
    _emit(report)
    return 0 if report.get("status") != "error" else 1


def cmd_register(args: argparse.Namespace) -> int:
    items = registry.register(args.workspace)
    _emit({"action": "register", "workspace": args.workspace, "workspaces": items})
    return 0


def cmd_unregister(args: argparse.Namespace) -> int:
    items = registry.unregister(args.workspace)
    _emit({"action": "unregister", "workspace": args.workspace, "workspaces": items})
    return 0


def cmd_list_workspaces(args: argparse.Namespace) -> int:
    _emit({"registry": str(registry.registry_path()), "workspaces": registry.list_workspaces()})
    return 0


def cmd_sync_all(args: argparse.Namespace) -> int:
    report = sync_all(apply=args.apply)
    _emit(report)
    return 0


def cmd_status_all(args: argparse.Namespace) -> int:
    report = sync_all(apply=False)
    report["view"] = "status"
    _emit(report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kanboard_plan_sync",
        description=(
            "Markdown-primary plan sync core. Markdown plans are the source of "
            "truth; Kanboard is a projection. All CLI commands are read-only / "
            "dry-run."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_inspect = sub.add_parser(
        "inspect-workspace", help="read-only report of workspace config/plans/state"
    )
    p_inspect.add_argument("workspace", help="workspace root directory")
    p_inspect.set_defaults(func=cmd_inspect_workspace)

    p_manifest = sub.add_parser(
        "build-manifest", help="parse a plan into an internal sync manifest (JSON)"
    )
    p_manifest.add_argument("plan_path", help="path to the Markdown plan document")
    p_manifest.add_argument("--workspace", help="workspace root for plan metadata")
    p_manifest.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="(default) build only; never writes",
    )
    p_manifest.set_defaults(func=cmd_build_manifest)

    p_diff = sub.add_parser(
        "diff", help="dry-run diff of plan vs sync state (planned operations)"
    )
    p_diff.add_argument("plan_path", help="path to the Markdown plan document")
    p_diff.add_argument("--workspace", help="workspace root for config + state")
    p_diff.set_defaults(func=cmd_diff)

    p_secrets = sub.add_parser(
        "check-secrets",
        help="verify no API token/credential is stored in config/state/plan files",
    )
    p_secrets.add_argument("workspace", help="workspace root directory")
    p_secrets.set_defaults(func=cmd_check_secrets)

    p_init = sub.add_parser(
        "init-workspace",
        help="scaffold .kanboard-plan.yml (+state) from discovered docs/plan/*.md",
    )
    p_init.add_argument("workspace", help="workspace root directory")
    p_init.add_argument(
        "--force", action="store_true", help="regenerate config even if it exists"
    )
    p_init.set_defaults(func=cmd_init_workspace)

    p_reg = sub.add_parser("register", help="add a workspace to the global registry")
    p_reg.add_argument("workspace", help="workspace root directory")
    p_reg.set_defaults(func=cmd_register)

    p_unreg = sub.add_parser(
        "unregister", help="remove a workspace from the global registry"
    )
    p_unreg.add_argument("workspace", help="workspace root directory")
    p_unreg.set_defaults(func=cmd_unregister)

    p_listws = sub.add_parser(
        "list-workspaces", help="list registered workspaces (read-only)"
    )
    p_listws.set_defaults(func=cmd_list_workspaces)

    p_syncall = sub.add_parser(
        "sync-all",
        help="dry-run (default) or --apply sync across all registered workspaces",
    )
    p_syncall.add_argument(
        "--apply",
        action="store_true",
        help="write to live Kanboard (otherwise dry-run only)",
    )
    p_syncall.set_defaults(func=cmd_sync_all)

    p_statall = sub.add_parser(
        "status-all", help="read-only planned-ops overview across registered workspaces"
    )
    p_statall.set_defaults(func=cmd_status_all)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
