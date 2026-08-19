"""Optional live dispatch into vendored mcp_bio."""

from __future__ import annotations

import json
import sys
from typing import Any

from gateway.paths import BIO_LIB


def call_bio_tool(tool: str, arguments: dict[str, Any] | None = None) -> str:
    """Call a vendored mcp_bio tool. Raises RuntimeError if the stack is unavailable."""
    if not BIO_LIB.is_dir():
        raise RuntimeError(f"vendored bio-tools lib missing: {BIO_LIB}")
    lib = str(BIO_LIB)
    if lib not in sys.path:
        sys.path.insert(0, lib)
    try:
        from mcp_bio.server import BioAggregate
    except Exception as exc:  # pragma: no cover - depends on optional vendor deps
        raise RuntimeError(
            "mcp_bio could not be imported. Install project deps with "
            "`uv sync --python 3.12` and keep vendor/wisp-science/mcp-servers/bio-tools."
        ) from exc

    agg = BioAggregate()
    args = dict(arguments or {})
    handler = getattr(agg, "t1_handlers", {}).get(tool)
    if handler is not None:
        result = handler(args)
        return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)

    fm = getattr(agg, "t2_fm", {}).get(tool)
    if fm is None:
        raise KeyError(f"unknown or deferred bio tool: {tool}")
    try:
        import anyio

        result = anyio.run(fm.call_tool, tool, args)
    except Exception as exc:  # pragma: no cover - live HTTP
        raise RuntimeError(f"bio tool {tool} failed: {exc}") from exc
    if isinstance(result, str):
        return result
    try:
        return json.dumps(result, ensure_ascii=False, default=str)
    except TypeError:
        return str(result)
