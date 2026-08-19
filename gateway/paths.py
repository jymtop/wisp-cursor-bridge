"""Resolve project, vendor, and Wisp app-data paths."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDOR_WISP = REPO_ROOT / "vendor" / "wisp-science"
BIO_LIB = VENDOR_WISP / "mcp-servers" / "bio-tools" / "lib"
DOMAINS_JSON = BIO_LIB / "mcp_bio" / "domains.json"
DEFERRED_JSON = BIO_LIB / "mcp_bio" / "deferred.json"
BUNDLED_SKILLS = VENDOR_WISP / "skills"


def project_root(override: str | Path | None = None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    env = os.environ.get("WISP_PROJECT_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "research" / "HANDOFF.md").is_file() or (
            candidate / "INTEROP.md"
        ).is_file():
            return candidate
    return cwd


def wisp_sqlite(root: Path | None = None) -> Path:
    return (root or project_root()) / ".wisp" / "wisp.sqlite"


def plugin_roots() -> list[Path]:
    roots: list[Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        roots.append(
            Path(appdata) / "science.wisp-science" / "wisp-science" / "plugins"
        )
    home = Path.home()
    roots.append(home / ".wisp" / "plugins")
    extra = os.environ.get("WISP_PLUGIN_ROOT")
    if extra:
        roots.append(Path(extra).expanduser())
    return roots
