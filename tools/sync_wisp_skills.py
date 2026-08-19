"""Mirror Wisp skills and plugin MCP into Cursor project files."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from gateway.paths import (
    BUNDLED_SKILLS,
    REPO_ROOT,
    app_wisp_sqlite,
    plugin_roots,
    project_root,
)

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
ADAPTER_SERVERS = {"wisp-bio", "wisp-history"}
COPY_IGNORE = shutil.ignore_patterns(".git", "__pycache__", "node_modules", ".Trash")


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


def _copy_skill_tree(src: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src / "SKILL.md", dest / "SKILL.md")
    for child in src.iterdir():
        if child.name == "SKILL.md" or child.name in {".git", "__pycache__", "node_modules"}:
            continue
        target = dest / child.name
        if child.is_dir():
            shutil.copytree(child, target, dirs_exist_ok=True, ignore=COPY_IGNORE)
        else:
            shutil.copy2(child, target)


def sync_skills(root: Path, extra_plugin_root: Path | None = None) -> list[str]:
    dest_root = root / ".cursor" / "skills"
    dest_root.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for skill_md in discover_skills(root, extra_plugin_root):
        name = _skill_name(skill_md)
        dest = dest_root / name
        if dest.exists() and _is_adapter_owned(dest):
            continue
        _copy_skill_tree(skill_md.parent, dest)
        copied.append(name)
    return copied


def _expand_plugin_vars(value: str, plugin_root: Path) -> str:
    text = str(plugin_root)
    return value.replace("${WISP_PLUGIN_ROOT}", text).replace("$WISP_PLUGIN_ROOT", text)


def _spec_from_mcp_server(server: dict, plugin_root: Path, plugin_id: str) -> dict | None:
    command = server.get("command")
    if not command:
        return None
    args = [_expand_plugin_vars(str(item), plugin_root) for item in (server.get("args") or [])]
    spec: dict = {
        "command": command,
        "args": args,
        "env": {"WISP_PLUGIN_ROOT": str(plugin_root)},
    }
    cwd = server.get("cwd")
    if cwd in (None, "", "."):
        spec["cwd"] = str(plugin_root)
    else:
        spec["cwd"] = _expand_plugin_vars(str(cwd), plugin_root)
    sid = str(server.get("id") or plugin_id)
    return {sid: spec}


def _plugin_mcp_servers(
    extra_plugin_root: Path | None = None,
    *,
    system: bool = True,
) -> dict[str, dict]:
    servers: dict[str, dict] = {}
    roots = list(plugin_roots()) if system else []
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
            plugin_root = manifest.parent.parent
            plugin_id = str(data.get("id") or plugin_root.name)
            mcp_path = plugin_root / ".mcp.json"
            if mcp_path.is_file():
                try:
                    mcp_data = json.loads(mcp_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    mcp_data = {}
                incoming = mcp_data.get("mcpServers") or {}
                if isinstance(incoming, dict):
                    servers.update(incoming)
            for server in data.get("mcp_servers") or []:
                if not isinstance(server, dict):
                    continue
                parsed = _spec_from_mcp_server(server, plugin_root, plugin_id)
                if parsed:
                    servers.update(parsed)
            command = data.get("mcp", {}).get("command")
            if command:
                servers[plugin_id] = {
                    "command": command,
                    "args": data.get("mcp", {}).get("args") or [],
                    "cwd": str(plugin_root),
                    "env": {"WISP_PLUGIN_ROOT": str(plugin_root)},
                }
    return servers


def adapter_mcp_servers(science_root: Path) -> dict[str, dict]:
    science = str(science_root.resolve())
    adapter = str(REPO_ROOT)
    history_env = {
        "WISP_PROJECT_ROOT": science,
    }
    app_db = app_wisp_sqlite()
    if app_db is not None:
        history_env["WISP_SQLITE"] = str(app_db)
    uv_args = [
        "run",
        "--directory",
        adapter,
        "--python",
        "3.12",
        "python",
        "-m",
    ]
    return {
        "wisp-bio": {
            "command": "uv",
            "args": [*uv_args, "gateway.wisp_bio_gateway"],
            "env": {
                "WISP_BIO_LIVE": "1",
                "WISP_PROJECT_ROOT": science,
                "NCBI_EMAIL": "wisp-cursor-bridge@users.noreply.github.com",
            },
        },
        "wisp-history": {
            "command": "uv",
            "args": [*uv_args, "gateway.wisp_history"],
            "env": history_env,
        },
    }


def write_mcp_json(
    dest: Path,
    science_root: Path,
    extra_plugin_root: Path | None = None,
    *,
    system_plugins: bool = True,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    servers = adapter_mcp_servers(science_root)
    for name, spec in _plugin_mcp_servers(extra_plugin_root, system=system_plugins).items():
        if name in ADAPTER_SERVERS:
            continue
        servers[name] = spec
    dest.write_text(
        json.dumps({"mcpServers": servers}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def merge_mcp_json(root: Path, extra_plugin_root: Path | None = None) -> None:
    write_mcp_json(root / ".cursor" / "mcp.json", root, extra_plugin_root)


def copy_adapter_overlay(science_root: Path) -> None:
    if science_root.resolve() == REPO_ROOT.resolve():
        return
    src_skills = REPO_ROOT / ".cursor" / "skills"
    dest_skills = science_root / ".cursor" / "skills"
    if src_skills.is_dir():
        dest_skills.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_skills, dest_skills, dirs_exist_ok=True, ignore=COPY_IGNORE)
    dest_rules = science_root / ".cursor" / "rules"
    dest_rules.mkdir(parents=True, exist_ok=True)
    for name in ("wisp-router.mdc", "wisp-bridge.mdc"):
        src_rule = REPO_ROOT / ".cursor" / "rules" / name
        if src_rule.is_file():
            shutil.copy2(src_rule, dest_rules / name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="", help="Cursor config root (default: adapter repo)")
    parser.add_argument("--science", default="", help="Wisp topic folder for WISP_PROJECT_ROOT")
    parser.add_argument("--plugin-root", default="", help="Extra plugin directory for tests")
    parser.add_argument(
        "--user-mcp",
        action="store_true",
        help="Also write ~/.cursor/mcp.json so this machine can approve the servers",
    )
    args = parser.parse_args(argv)
    root = project_root(args.project or None)
    science = Path(args.science).expanduser().resolve() if args.science else root
    extra = Path(args.plugin_root).expanduser() if args.plugin_root else None
    copied = sync_skills(root, extra)
    write_mcp_json(root / ".cursor" / "mcp.json", science, extra)
    if science != root:
        sync_skills(science, extra)
        copy_adapter_overlay(science)
        write_mcp_json(science / ".cursor" / "mcp.json", science, extra)
    if args.user_mcp:
        user_mcp = Path.home() / ".cursor" / "mcp.json"
        write_mcp_json(user_mcp, science, extra)
        print("user mcp:", user_mcp)
    print("synced:", ", ".join(copied) or "(no new skills)")
    print("science:", science)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
