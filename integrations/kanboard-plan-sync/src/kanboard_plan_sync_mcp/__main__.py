"""Entry point for the plan-centric MCP server.

``--list-tools`` prints the registered plan-centric tool names and exits; it
works without the MCP SDK installed and is used as the smoke test. With no
flag, the stdio MCP server runs (requires the ``mcp`` SDK).
"""

from __future__ import annotations

import argparse
import json
import sys

from .tools import PLAN_TOOLS, tool_names


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kanboard_plan_sync_mcp",
        description="Plan-centric MCP facade for kanboard-plan-sync.",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="print registered plan-centric tools as JSON and exit (no SDK needed)",
    )
    args = parser.parse_args(argv)

    if args.list_tools:
        print(
            json.dumps(
                {
                    "server": "kanboard-plan-sync",
                    "tools": [
                        {"name": spec.name, "description": spec.description}
                        for spec in PLAN_TOOLS
                    ],
                    "tool_names": tool_names(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    try:
        import asyncio

        from .server import serve

        asyncio.run(serve())
        return 0
    except ImportError as exc:
        print(
            f"MCP SDK not available ({exc}); install with: pip install 'mcp>=1.0'",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
