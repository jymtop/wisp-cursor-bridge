"""Let vendored bio-tools import ToolError after MCP 2.0 dropped FastMCP."""

from __future__ import annotations

import sys
import types


class ToolError(Exception):
    """Stand-in for mcp.server.fastmcp.exceptions.ToolError."""


def install_fastmcp_compat() -> None:
    if "mcp.server.fastmcp.exceptions" in sys.modules:
        return
    exceptions = types.ModuleType("mcp.server.fastmcp.exceptions")
    exceptions.ToolError = ToolError
    parent = types.ModuleType("mcp.server.fastmcp")
    parent.exceptions = exceptions
    parent.FastMCP = None
    sys.modules.setdefault("mcp.server.fastmcp", parent)
    sys.modules["mcp.server.fastmcp.exceptions"] = exceptions
