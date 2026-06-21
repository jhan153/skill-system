"""MCP server wiring.

The MCP SDK is imported lazily inside :func:`build_server` / :func:`serve` so
that importing this module (and listing tools) works even when the SDK is not
installed. Only the plan-centric tools from :mod:`.tools` are registered.
"""

from __future__ import annotations

import json

from . import __version__
from .tools import PLAN_TOOLS, run_tool

SERVER_NAME = "kanboard-plan-sync"


def build_server():
    """Build a low-level MCP Server exposing only plan-centric tools."""
    from mcp.server import Server
    import mcp.types as types

    server = Server(SERVER_NAME, version=__version__)

    @server.list_tools()
    async def handle_list_tools():
        return [
            types.Tool(
                name=spec.name,
                description=spec.description,
                inputSchema=spec.input_schema,
            )
            for spec in PLAN_TOOLS
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict | None):
        result = run_tool(name, arguments or {})
        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    return server


async def serve() -> None:
    """Run the server over stdio (requires the ``mcp`` SDK)."""
    from mcp.server.stdio import stdio_server

    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )
