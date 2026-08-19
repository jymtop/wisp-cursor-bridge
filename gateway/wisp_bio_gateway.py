"""stdio MCP gateway: 3 tools in front of ~247 Wisp bio-tools."""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server.mcpserver import MCPServer

from gateway.bio_backend import call_bio_tool
from gateway.bio_catalog import load_catalog

mcp = MCPServer("wisp-bio")
_CATALOG = load_catalog()


@mcp.tool()
def list_bio_domains() -> str:
    """List Wisp bio-tools domains (PubMed, expression, structures, ...)."""
    rows = []
    for domain in _CATALOG.domain_names():
        tools = [name for name in _CATALOG.domains[domain] if name not in _CATALOG.deferred_tools]
        rows.append({"domain": domain, "tool_count": len(tools)})
    return json.dumps({"schema": "wisp.bio.domains.v1", "domains": rows}, ensure_ascii=False)


@mcp.tool()
def search_bio_tools(query: str, domain: str = "", limit: int = 20) -> str:
    """Search bio-tools by keyword and optional domain slug. Does not load full schemas."""
    hits = _CATALOG.search(query, domain=domain or None, limit=max(1, min(limit, 50)))
    return json.dumps(
        {
            "schema": "wisp.bio.search.v1",
            "query": query,
            "domain": domain or None,
            "hits": [{"domain": d, "tool": t} for d, t in hits],
        },
        ensure_ascii=False,
    )


@mcp.tool()
def use_bio_tool(tool: str, arguments_json: str = "{}") -> str:
    """Call one bio-tool by name. arguments_json is a JSON object."""
    domain = _CATALOG.resolve(tool)
    if domain is None:
        if tool in _CATALOG.deferred_tools:
            return json.dumps(
                {
                    "ok": False,
                    "error": "deferred_license",
                    "tool": tool,
                    "hint": "KEGG / CADD / PanglaoDB / Cell Model Passports stay off.",
                },
                ensure_ascii=False,
            )
        return json.dumps({"ok": False, "error": "unknown_tool", "tool": tool}, ensure_ascii=False)

    try:
        arguments: dict[str, Any] = json.loads(arguments_json or "{}")
        if not isinstance(arguments, dict):
            raise ValueError("arguments_json must be a JSON object")
    except (json.JSONDecodeError, ValueError) as exc:
        return json.dumps({"ok": False, "error": "bad_arguments", "detail": str(exc)}, ensure_ascii=False)

    if os.environ.get("WISP_BIO_LIVE", "0") not in {"1", "true", "yes"}:
        return json.dumps(
            {
                "ok": False,
                "error": "live_disabled",
                "tool": tool,
                "domain": domain,
                "hint": "Set WISP_BIO_LIVE=1 to call vendored mcp_bio (network).",
                "arguments": arguments,
            },
            ensure_ascii=False,
        )

    try:
        payload = call_bio_tool(tool, arguments)
    except Exception as exc:
        return json.dumps(
            {"ok": False, "error": "call_failed", "tool": tool, "detail": str(exc)},
            ensure_ascii=False,
        )
    return json.dumps({"ok": True, "tool": tool, "domain": domain, "result": payload}, ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
