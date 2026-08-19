"""Mirror Wisp skills and plugin MCP into Cursor project files."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from gateway.paths import BUNDLED_SKILLS, plugin_roots, project_root

SKIP_SKILLS = {
    "self-awareness",
    "custom-theme",
    "customize",
    "agent-infini",
    "bear-counter",
    "bear-map",
    "bear-onboard",
    "bear-propose",
    "bear-review",
    "bear-scoop",
    "bear-support",
    "bear-trace",
}

ADAPTER_MARKER = "wisp-cursor-adapter: true"


def _skill_name(skill_md: Path) -> str:
    return skill_md.parent.name


def discover_skills(root: Path, extra_plugin_root: Path | None = None) -> list[Path]:
    found: list[Path] = []
    search_roots = [
        BUNDLED_SKILLS,
        root / ".wisp" / "skills",
        Path.home() / ".wisp" / "skills",
    ]
    for plugin_root in plugin_roots():
        search_roots.append(plugin_root)
    if extra_plugin_root:
        search_roots.append(extra_plugin_root)
    seen: set[str] = set()
    for base in search_roots:
        if not base.is_dir():
            continue
        for skill_md in base.rglob("SKILL.md"):
            name = _skill_name(skill_md)
            if name in SKIP_SKILLS or name in seen:
                continue
            seen.add(name)
            found.append(skill_md)
    return found


def _is_adapter_owned(dest: Path) -> bool:
    skill = dest / "SKILL.md"
    if not skill.is_file():
        return False
    return ADAPTER_MARKER in skill.read_text(encoding="utf-8", errors="replace")


def sync_skills(root: Path, extra_plugin_root: Path | None = None) -> list[str]:
    dest_root = root / ".cursor" / "skills"
    dest_root.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for skill_md in discover_skills(root, extra_plugin_root):
        name = _skill_name(skill_md)
        dest = dest_root / name
        if dest.exists() and _is_adapter_owned(dest):
            continue
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / "SKILL.md"
        shutil.copy2(skill_md, target)
        copied.append(name)
    return copied


def _plugin_mcp_servers(extra_plugin_root: Path | None = None) -> dict[str, dict]:
    servers: dict[str, dict] = {}
    roots = list(plugin_roots())
    if extra_plugin_root:
        roots.append(extra_plugin_root)
    for base in roots:
        if not base.is_dir():
            continue
        for manifest in base.rglob("plugin.json"):
            if manifest.parent.name not in {".wisp-plugin", ".claude-plugin"}:
                continue
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            mcp_path = manifest.parent.parent / ".mcp.json"
            if mcp_path.is_file():
                try:
                    mcp_data = json.loads(mcp_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                incoming = mcp_data.get("mcpServers") or {}
                if isinstance(incoming, dict):
                    servers.update(incoming)
            plugin_id = data.get("id") or manifest.parent.parent.name
            command = data.get("mcp", {}).get("command")
            if command:
                servers[str(plugin_id)] = {
                    "command": command,
                    "args": data.get("mcp", {}).get("args") or [],
                }
    return servers


def merge_mcp_json(root: Path, extra_plugin_root: Path | None = None) -> None:
    path = root / ".cursor" / "mcp.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    current: dict = {"mcpServers": {}}
    if path.is_file():
        try:
            current = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            current = {"mcpServers": {}}
    servers = current.setdefault("mcpServers", {})
    for name, spec in _plugin_mcp_servers(extra_plugin_root).items():
        if name in {"wisp-bio", "wisp-history"}:
            continue
        servers[name] = spec
    path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="", help="Project root (default: auto)")
    parser.add_argument("--plugin-root", default="", help="Extra plugin directory for tests")
    args = parser.parse_args(argv)
    root = project_root(args.project or None)
    extra = Path(args.plugin_root).expanduser() if args.plugin_root else None
    copied = sync_skills(root, extra)
    merge_mcp_json(root, extra)
    print("synced:", ", ".join(copied) or "(no new skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
