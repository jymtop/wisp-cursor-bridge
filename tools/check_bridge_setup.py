# -*- coding: utf-8 -*-
"""
============================================================================
01 | Portable Wisp-Cursor bridge setup check
============================================================================
Script   : check_bridge_setup.py
Purpose  : Print a human- and agent-readable prompt list so a new clone
           can finish Cursor / Claude Code setup (local git init, overlay,
           MCP approve). Git check = is `git` installed and has `git init`
           already happened? Adapter vs topic = files, not `git remote`.
Question : Has this folder been `git init`'d, and what should the user
           do next (local history only — never ask them to push)?
Stage    : Onboarding / first open
Input    : cwd or --path; optional env WISP_TOPICS_ROOT / WISP_ADAPTER_ROOT;
           optional .wisp/topics-root.local (one path line)
Output   : stdout report; exit 0 unless the git binary is missing so the
           work-tree check cannot run
Figure   : (this script does not produce figures)
Status   : draft
---------------------------------------------------------------------------
边界声明：本脚本【只探测并打印清单】；这里【不】写入 mcp.json、
          不跑 uv sync、不 init/commit/push、不读取 live sqlite。
          本地 git 只用于跟踪改动和回滚，不要求设置 origin。
============================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

BRIDGE_REPO_NAME = "wisp-cursor-bridge"
CANONICAL_CLONE = "https://github.com/jymtop/wisp-cursor-bridge"
LOCAL_TOPICS_FILE = Path(".wisp") / "topics-root.local"
ADAPTER_FILES = ("INTEROP.md",)
ADAPTER_DIRS = ("gateway",)
ADAPTER_SCRIPTS = (Path("tools") / "sync_wisp_skills.py",)
GIT_INIT_PROMPT = (
    "This folder is not a git repository yet (尚未 git init). "
    "Run `git init` here to track local changes and make rollback easy. "
    f"If you meant to use the adapter, clone {CANONICAL_CLONE} instead. "
    "Local git is enough; a remote is not required."
)
GIT_INITIALIZED_PROMPT = (
    "Already a git repository (已 git init). "
    "Local git is for tracking changes and easy rollback."
)


@dataclass
class PromptItem:
    key: str
    text: str
    status: str = "todo"  # todo | ok | info


@dataclass
class SetupReport:
    mode: str
    cwd: Path
    git_found: bool
    is_work_tree: bool
    origin: str | None
    is_adapter: bool
    prompts: list[PromptItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    facts: dict[str, str] = field(default_factory=dict)
    exit_code: int = 0

    def has_prompt(self, key: str, status: str | None = None) -> bool:
        for item in self.prompts:
            if item.key == key and (status is None or item.status == status):
                return True
        return False


GitRun = Callable[[list[str], Path], tuple[int, str, str]]


def _auto_git_exe() -> str | None:
    return shutil.which("git")


def _default_run_git(git_exe: str) -> GitRun:
    def _run(args: list[str], cwd: Path) -> tuple[int, str, str]:
        try:
            proc = subprocess.run(
                [git_exe, *args],
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except OSError as exc:
            return 1, "", str(exc)
        return proc.returncode, proc.stdout or "", proc.stderr or ""

    return _run


def normalize_remote(url: str) -> str:
    text = url.strip().replace("\\", "/")
    if text.endswith(".git"):
        text = text[:-4]
    if text.startswith("git@"):
        text = text[4:].replace(":", "/", 1)
    for prefix in ("ssh://git@", "ssh://", "git://", "https://", "http://"):
        if text.lower().startswith(prefix):
            text = text[len(prefix) :]
            break
    return text.strip("/").lower()


def is_bridge_remote(url: str | None) -> bool:
    if not url:
        return False
    normalized = normalize_remote(url)
    return normalized == BRIDGE_REPO_NAME or normalized.endswith(f"/{BRIDGE_REPO_NAME}")


def looks_like_adapter(root: Path) -> bool:
    if not all((root / name).is_file() for name in ADAPTER_FILES):
        return False
    if not all((root / name).is_dir() for name in ADAPTER_DIRS):
        return False
    return all((root / name).is_file() for name in ADAPTER_SCRIPTS)


def has_dot_git(root: Path) -> bool:
    return (root / ".git").exists()


def read_topics_root(
    start: Path,
    environ: Mapping[str, str] | None = None,
) -> Path | None:
    env = (environ if environ is not None else os.environ).get("WISP_TOPICS_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    for candidate in (start.resolve(), *start.resolve().parents):
        local = candidate / LOCAL_TOPICS_FILE
        if not local.is_file():
            continue
        for raw in local.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            return Path(line).expanduser().resolve()
    return None


def is_under_topics_root(path: Path, topics_root: Path | None) -> bool:
    if topics_root is None:
        return False
    try:
        path.resolve().relative_to(topics_root.resolve())
    except ValueError:
        return False
    return True


def mcp_has_server(mcp_path: Path, name: str = "wisp-bio") -> bool:
    if not mcp_path.is_file():
        return False
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    servers = data.get("mcpServers")
    return isinstance(servers, dict) and name in servers


def pyproject_looks_accidental(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return "wisp-cursor-bridge" in text or "wisp-bio-gateway" in text


def infer_adapter_root(
    checked: Path,
    environ: Mapping[str, str] | None = None,
) -> Path | None:
    env = (environ if environ is not None else os.environ).get("WISP_ADAPTER_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve().parent.parent
    if looks_like_adapter(here):
        return here
    if looks_like_adapter(checked):
        return checked.resolve()
    return None


def overlay_command(adapter: Path | None, science: Path) -> str:
    adapter_s = str(adapter) if adapter is not None else "<adapter-repo>"
    return (
        f'uv run --directory "{adapter_s}" --python 3.12 '
        f'python -m tools.sync_wisp_skills --science "{science}"'
    )


def _git_text(run_git: GitRun, args: list[str], cwd: Path) -> str | None:
    code, stdout, _stderr = run_git(args, cwd)
    if code != 0:
        return None
    return stdout.strip()


def parse_ahead_behind(status_sb: str) -> tuple[int, int] | None:
    ahead_m = re.search(r"ahead (\d+)", status_sb)
    behind_m = re.search(r"behind (\d+)", status_sb)
    if not ahead_m and not behind_m:
        return None
    ahead = int(ahead_m.group(1)) if ahead_m else 0
    behind = int(behind_m.group(1)) if behind_m else 0
    return ahead, behind


def run_check(
    path: Path,
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    fetch: bool = False,
    git_exe: str | None = "",
    run_git: GitRun | None = None,
) -> SetupReport:
    """Inspect *path* and return a prompt list. Never writes files."""
    env = environ if environ is not None else os.environ
    root = path.expanduser().resolve()
    report = SetupReport(
        mode="unknown",
        cwd=root,
        git_found=False,
        is_work_tree=False,
        origin=None,
        is_adapter=False,
    )
    report.facts["cwd"] = str(root)
    if sys.version_info[:2] != (3, 12):
        report.warnings.append(
            f"Python {sys.version_info.major}.{sys.version_info.minor} is active; "
            "use 3.12 (`uv run --python 3.12`)."
        )
        report.facts["python"] = f"{sys.version_info.major}.{sys.version_info.minor}"

    adapter_by_files = looks_like_adapter(root)
    topics_root = read_topics_root(root, env)
    if topics_root is not None:
        report.facts["topics_root"] = str(topics_root)
        report.facts["under_topics_root"] = (
            "yes" if is_under_topics_root(root, topics_root) else "no"
        )

    resolved_git = _auto_git_exe() if git_exe == "" else git_exe
    report.git_found = bool(resolved_git)
    report.facts["git"] = "found" if report.git_found else "missing"

    if not report.git_found:
        report.exit_code = 1
        report.prompts.append(
            PromptItem(
                "INSTALL_GIT",
                "Install a `git` executable so this check can tell whether "
                "`git init` has been done, then reopen this folder. "
                f"If you meant to use the adapter, clone {CANONICAL_CLONE}.",
            )
        )
        if adapter_by_files:
            report.mode = "adapter"
            report.is_adapter = True
            report.prompts.append(
                PromptItem(
                    "ADAPTER_NOT_SCIENCE",
                    "This folder looks like the bridge adapter "
                    "(INTEROP.md + gateway/ + tools/sync_wisp_skills.py). "
                    "Do science in a topic folder, not here.",
                    "info",
                )
            )
            _add_adapter_setup_prompts(report, home)
        else:
            report.mode = "unknown"
            report.prompts.append(PromptItem("GIT_INIT", GIT_INIT_PROMPT))
        return report

    runner = run_git if run_git is not None else _default_run_git(resolved_git or "git")
    inside = _git_text(runner, ["rev-parse", "--is-inside-work-tree"], root)
    report.is_work_tree = inside == "true" or has_dot_git(root)
    report.facts["work_tree"] = "yes" if report.is_work_tree else "no"
    report.facts["git_init"] = "yes" if report.is_work_tree else "no"

    if not report.is_work_tree:
        report.prompts.append(PromptItem("GIT_INIT", GIT_INIT_PROMPT))
        if adapter_by_files:
            report.mode = "adapter"
            report.is_adapter = True
            _add_adapter_setup_prompts(report, home)
        else:
            report.mode = "unknown"
        return report

    report.prompts.append(
        PromptItem("GIT_INITIALIZED", GIT_INITIALIZED_PROMPT, "ok")
    )

    toplevel = _git_text(runner, ["rev-parse", "--show-toplevel"], root)
    if toplevel:
        root = Path(toplevel)
        report.cwd = root
        report.facts["cwd"] = str(root)
        adapter_by_files = looks_like_adapter(root)

    origin = _git_text(runner, ["remote", "get-url", "origin"], root)
    report.origin = origin or None
    report.facts["origin"] = origin or "(none)"
    adapter_by_remote = is_bridge_remote(origin)
    # Files are the adapter definition; remote URL is only a weak extra hint.
    report.is_adapter = adapter_by_files or adapter_by_remote
    report.facts["adapter_by_remote"] = "yes" if adapter_by_remote else "no"
    report.facts["adapter_by_files"] = "yes" if adapter_by_files else "no"

    if fetch:
        runner(["fetch", "--quiet"], root)

    status_sb = _git_text(runner, ["status", "-sb"], root) or ""
    report.facts["git_status"] = status_sb.splitlines()[0] if status_sb else ""
    head = _git_text(runner, ["rev-parse", "--abbrev-ref", "HEAD"], root) or ""
    report.facts["head"] = head
    if head == "HEAD":
        report.warnings.append(
            "Detached HEAD. Check out a local branch (usually `main`) "
            "if you need a named line of history."
        )

    counts = parse_ahead_behind(status_sb)
    if counts is None:
        upstream = _git_text(
            runner,
            ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            root,
        )
        if upstream:
            pair = _git_text(
                runner,
                ["rev-list", "--left-right", "--count", f"{upstream}...HEAD"],
                root,
            )
            if pair:
                left, _, right = pair.partition("\t")
                if left.isdigit() and right.isdigit():
                    counts = (int(right), int(left))
    if counts is not None:
        ahead, behind = counts
        report.facts["ahead"] = str(ahead)
        report.facts["behind"] = str(behind)

    if report.is_adapter:
        report.mode = "adapter"
        _fill_adapter(report, home)
        return report

    report.mode = "topic"
    _fill_topic(report, root, env, home)
    return report


def _add_adapter_setup_prompts(report: SetupReport, home: Path | None) -> None:
    report.prompts.append(
        PromptItem(
            "ADAPTER_UV_SYNC_OK",
            "`uv sync --python 3.12` is OK in this adapter repo only. "
            "Never run `uv sync` in a science topic folder.",
            "info",
        )
    )
    report.prompts.append(
        PromptItem(
            "APPROVE_MCP",
            "Approve MCP servers `wisp-bio`, `wisp-history`, and `figure-library` "
            "in Cursor Settings → Tools & MCP.",
        )
    )
    report.prompts.append(
        PromptItem(
            "OPTIONAL_TOPICS_ROOT",
            "Optional: set env `WISP_TOPICS_ROOT` or write one absolute path "
            f"line in `{LOCAL_TOPICS_FILE.as_posix()}` (gitignored). "
            "Workspaces under that root auto-qualify as WS topic folders.",
            "info",
        )
    )
    report.prompts.append(
        PromptItem(
            "OPTIONAL_USER_RULE",
            "Optional: after you copy `.cursor/skills/ws-continue/SKILL.md` to "
            "`~/.cursor/skills/ws-continue/SKILL.md` (or after the first overlay), "
            "add a short User Rule that points at that skill. Do not paste "
            "someone else's personal rules.",
            "info",
        )
    )
    _user_mcp_prompt(report, home)


def _fill_adapter(report: SetupReport, home: Path | None) -> None:
    report.prompts.append(
        PromptItem(
            "ADAPTER_NOT_SCIENCE",
            "You opened the bridge adapter repo "
            "(INTEROP.md + gateway/ + tools/sync_wisp_skills.py). "
            "Do science in a *topic folder*, not here. "
            f"`uv sync --python 3.12` is OK here only. Clone URL: {CANONICAL_CLONE}",
            "info",
        )
    )
    _add_adapter_setup_prompts(report, home)


def _fill_topic(
    report: SetupReport,
    root: Path,
    environ: Mapping[str, str],
    home: Path | None,
) -> None:
    adapter = infer_adapter_root(root, environ)
    mcp = root / ".cursor" / "mcp.json"
    has_bio = mcp_has_server(mcp, "wisp-bio")
    report.facts["overlay_wisp_bio"] = "yes" if has_bio else "no"
    if has_bio:
        report.prompts.append(
            PromptItem(
                "RUN_OVERLAY",
                "Overlay is present (`.cursor/mcp.json` has `wisp-bio`). "
                "Do not re-run sync unless the overlay is missing.",
                "ok",
            )
        )
    else:
        cmd = overlay_command(adapter, root)
        if home is not None:
            user_mcp = home / ".cursor" / "mcp.json"
        else:
            user_mcp = Path.home() / ".cursor" / "mcp.json"
        extra = ""
        if not mcp_has_server(user_mcp, "wisp-bio"):
            extra = (
                " Pass `--user-mcp` only if this machine has no `wisp-bio` "
                "in `~/.cursor/mcp.json` yet."
            )
        report.prompts.append(
            PromptItem(
                "RUN_OVERLAY",
                "This looks like a science topic folder without the bridge overlay. "
                f"Run:\n    {cmd}\n"
                "Then Reload Window. Never `uv sync` here. Never add `pyproject.toml` here."
                + extra,
            )
        )
        report.prompts.append(
            PromptItem(
                "RELOAD_WINDOW",
                "After the first overlay, Reload Window so project skills and MCP appear.",
            )
        )
    report.prompts.append(
        PromptItem(
            "NO_UV_SYNC_IN_TOPIC",
            "Never run `uv sync` in this topic folder. Never add `pyproject.toml` here.",
            "ok" if not (root / "pyproject.toml").is_file() else "info",
        )
    )
    if pyproject_looks_accidental(root / "pyproject.toml"):
        report.warnings.append(
            "This topic folder has a `pyproject.toml` that looks copied from "
            "the adapter (`wisp-cursor-bridge`). That is usually accidental — "
            "do not treat this folder as the adapter."
        )
    if is_under_topics_root(root, read_topics_root(root, environ)):
        report.prompts.append(
            PromptItem(
                "PATH_TRIGGER",
                "This workspace is under `WISP_TOPICS_ROOT` / "
                f"`{LOCAL_TOPICS_FILE.as_posix()}`, so it auto-qualifies as a "
                "WS topic folder even without a spoken trigger.",
                "info",
            )
        )
    report.prompts.append(
        PromptItem(
            "TRIGGERS",
            "Spoken triggers still work anywhere: 继续WS任务 / 接上Wisp桥 / "
            "读HANDOFF继续 / 这是WS任务，帮我… / continue the WS task / "
            "wire the wisp bridge. Then follow `.cursor/skills/ws-continue/SKILL.md`.",
            "info",
        )
    )
    _user_mcp_prompt(report, home)


def _user_mcp_prompt(report: SetupReport, home: Path | None) -> None:
    user_home = home if home is not None else Path.home()
    user_mcp = user_home / ".cursor" / "mcp.json"
    if mcp_has_server(user_mcp, "wisp-bio"):
        report.facts["user_mcp_wisp_bio"] = "yes"
        report.prompts.append(
            PromptItem(
                "USER_MCP_OPTIONAL",
                "`~/.cursor/mcp.json` already has `wisp-bio`. "
                "Do not pass `--user-mcp` as a default.",
                "ok",
            )
        )
    else:
        report.facts["user_mcp_wisp_bio"] = "no"
        report.prompts.append(
            PromptItem(
                "USER_MCP_OPTIONAL",
                "Optional once: pass `--user-mcp` on overlay only if "
                "`~/.cursor/mcp.json` has no `wisp-bio` yet.",
                "info",
            )
        )


def format_report(report: SetupReport) -> str:
    lines = [
        "Wisp-Cursor bridge setup check",
        "==============================",
        f"cwd: {report.cwd}",
        f"mode: {report.mode}",
        f"git: {'found' if report.git_found else 'missing'}",
        f"git_init: {'yes' if report.is_work_tree else 'no'}",
        f"work_tree: {'yes' if report.is_work_tree else 'no'}",
        f"adapter: {'yes' if report.is_adapter else 'no'}",
        "",
        "PROMPTS",
        "-------",
    ]
    if not report.prompts:
        lines.append("(none)")
    for item in report.prompts:
        mark = {"todo": "[ ]", "ok": "[x]", "info": "[i]"}[item.status]
        text = item.text.replace("\n", "\n    ")
        lines.append(f"{mark} {item.key}: {text}")
    lines.extend(["", "WARNINGS", "--------"])
    if report.warnings:
        for warning in report.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("(none)")
    lines.extend(["", "NEXT", "----"])
    if not report.git_found:
        lines.append(
            "Install git so this check can tell whether `git init` has been done."
        )
    elif not report.is_work_tree:
        lines.append(
            "Run `git init` here for local history and rollback, or clone the "
            "adapter if that is what you meant."
        )
    elif report.mode == "adapter":
        lines.append(
            "This is the adapter clone. Finish the checklist above; do not do science here."
        )
    elif report.mode == "topic":
        if report.has_prompt("RUN_OVERLAY", "todo"):
            lines.append(
                "Run the overlay command, then Reload Window, then say a WS trigger "
                "or follow HANDOFF."
            )
        else:
            lines.append(
                "Overlay looks present. Follow ws-continue / research/HANDOFF.md "
                "for science work."
            )
    else:
        lines.append(
            "Run `git init` here for local history and rollback, or clone the "
            "adapter if that is what you meant."
        )
    lines.append(f"exit: {report.exit_code}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Print a Wisp-Cursor bridge setup prompt list "
            "(local git-init check + overlay)."
        )
    )
    parser.add_argument(
        "--path",
        default="",
        help="Folder to inspect (default: current working directory)",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Optional network fetch for maintainers of this adapter clone.",
    )
    args = parser.parse_args(argv)
    target = Path(args.path) if args.path else Path.cwd()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    report = run_check(target, fetch=args.fetch)
    sys.stdout.write(format_report(report))
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
