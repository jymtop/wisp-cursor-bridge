"""Read-only MCP over a Wisp project sqlite (never writes)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from gateway.paths import project_root, wisp_sqlite

mcp = MCPServer("wisp-history")


def _connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.is_file():
        raise FileNotFoundError(str(db_path))
    uri = db_path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _db(project: str = "") -> Path:
    return wisp_sqlite(project_root(project or None))


@mcp.tool()
def list_wisp_sessions(project_root_path: str = "", limit: int = 20) -> str:
    """List Wisp conversation frames from .wisp/wisp.sqlite (read-only)."""
    path = _db(project_root_path)
    if not path.is_file():
        return f"no sqlite at {path}"
    conn = _connect(path)
    try:
        rows = conn.execute(
            """
            SELECT id, agent_name, status, model, created_at, updated_at
            FROM frames
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (max(1, min(limit, 100)),),
        ).fetchall()
    finally:
        conn.close()
    if not rows:
        return "no frames"
    lines = [f"{r['id']}\t{r['status']}\t{r['model'] or '-'}\t{r['agent_name']}" for r in rows]
    return "\n".join(lines)


@mcp.tool()
def get_wisp_transcript(frame_id: str, project_root_path: str = "", max_chars: int = 8000) -> str:
    """Return user/assistant text for one Wisp frame (read-only, truncated)."""
    path = _db(project_root_path)
    if not path.is_file():
        return f"no sqlite at {path}"
    conn = _connect(path)
    try:
        rows = conn.execute(
            """
            SELECT seq, role, content
            FROM messages
            WHERE frame_id = ?
            ORDER BY seq ASC
            """,
            (frame_id,),
        ).fetchall()
    finally:
        conn.close()
    if not rows:
        return f"no messages for {frame_id}"
    parts: list[str] = []
    used = 0
    budget = max(500, min(max_chars, 20000))
    for row in rows:
        text = (row["content"] or "").strip()
        if not text:
            continue
        chunk = f"## {row['role']} (seq {row['seq']})\n{text}\n"
        if used + len(chunk) > budget:
            parts.append("\n[truncated]\n")
            break
        parts.append(chunk)
        used += len(chunk)
    return "".join(parts) or "empty transcript"


@mcp.tool()
def list_wisp_artifacts(project_root_path: str = "", limit: int = 30) -> str:
    """List artifact filenames recorded by Wisp (read-only)."""
    path = _db(project_root_path)
    if not path.is_file():
        return f"no sqlite at {path}"
    conn = _connect(path)
    try:
        rows = conn.execute(
            """
            SELECT filename, content_type, storage_path
            FROM artifacts
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (max(1, min(limit, 100)),),
        ).fetchall()
    finally:
        conn.close()
    if not rows:
        return "no artifacts"
    return "\n".join(f"{r['filename']}\t{r['content_type']}\t{r['storage_path']}" for r in rows)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
