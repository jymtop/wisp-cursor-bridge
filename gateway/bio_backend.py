"""Optional live dispatch into vendored mcp_bio (tier-1 without FastMCP)."""

from __future__ import annotations

import importlib
import json
import sys
from typing import Any

from gateway.fastmcp_compat import install_fastmcp_compat
from gateway.paths import BIO_LIB


def _ensure_lib() -> None:
    if not BIO_LIB.is_dir():
        raise RuntimeError(f"vendored bio-tools lib missing: {BIO_LIB}")
    lib = str(BIO_LIB)
    if lib not in sys.path:
        sys.path.insert(0, lib)
    install_fastmcp_compat()


def _domain_package(domain: str) -> str:
    return "mcp_" + domain.replace("-", "_")


def _call_domain_handler(domain: str, tool: str, arguments: dict[str, Any]) -> str:
    _ensure_lib()
    pkg = _domain_package(domain)
    try:
        mod = importlib.import_module(f"{pkg}.server")
    except Exception as exc:
        raise RuntimeError(
            f"could not import {pkg}.server (MCP 2.0 has no FastMCP for some "
            f"tier-2 domains). Tool={tool} domain={domain}: {exc}"
        ) from exc
    handlers = getattr(mod, "HANDLERS", None)
    if isinstance(handlers, dict) and tool in handlers:
        result = handlers[tool](arguments)
    elif callable(getattr(mod, tool, None)):
        result = getattr(mod, tool)(arguments)
    else:
        raise KeyError(f"unknown or deferred bio tool: {tool}")
    if isinstance(result, str):
        return result
    try:
        return json.dumps(result, ensure_ascii=False, default=str)
    except TypeError:
        return str(result)


def call_bio_tool(tool: str, arguments: dict[str, Any] | None = None) -> str:
    """Call one vendored bio-tool. Raises RuntimeError if the stack is unavailable."""
    from gateway.bio_catalog import load_catalog

    args = dict(arguments or {})
    domain = load_catalog().resolve(tool)
    if domain is None:
        raise KeyError(f"unknown or deferred bio tool: {tool}")
    return _call_domain_handler(domain, tool, args)
