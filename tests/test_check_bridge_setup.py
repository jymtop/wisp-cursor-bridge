from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools.check_bridge_setup import (
    format_report,
    is_bridge_remote,
    looks_like_adapter,
    parse_ahead_behind,
    pyproject_looks_accidental,
    read_topics_root,
    run_check,
)

_FORBIDDEN_USER_PHRASES = ("git push", "set origin", "publish this topic")


def _assert_no_publish_prompts(text: str) -> None:
    lowered = text.lower()
    for phrase in _FORBIDDEN_USER_PHRASES:
        assert phrase not in lowered


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-c",
            "user.email=bridge-test@example.com",
            "-c",
            "user.name=Bridge Test",
            *args,
        ],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _init_repo(path: Path, *, remote: str | None = None) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-b", "main")
    (path / "README.md").write_text("tmp\n", encoding="utf-8")
    _git(path, "add", "README.md")
    _git(path, "commit", "-m", "init")
    if remote:
        _git(path, "remote", "add", "origin", remote)
    return path


def _adapter_markers(path: Path) -> None:
    (path / "INTEROP.md").write_text("# interop\n", encoding="utf-8")
    (path / "gateway").mkdir(parents=True, exist_ok=True)
    (path / "tools").mkdir(parents=True, exist_ok=True)
    (path / "tools" / "sync_wisp_skills.py").write_text("# sync\n", encoding="utf-8")


def test_is_bridge_remote_canonical_and_forks() -> None:
    assert is_bridge_remote("https://github.com/jymtop/wisp-cursor-bridge.git")
    assert is_bridge_remote("git@github.com:alice/wisp-cursor-bridge.git")
    assert is_bridge_remote("https://github.com/alice/wisp-cursor-bridge")
    assert not is_bridge_remote("https://github.com/jymtop/wisp-cursor-bridge-docs")
    assert not is_bridge_remote("https://github.com/example/other-repo.git")


def test_parse_ahead_behind() -> None:
    assert parse_ahead_behind("## main...origin/main [behind 2]") == (0, 2)
    assert parse_ahead_behind("## main...origin/main [ahead 1, behind 3]") == (1, 3)
    assert parse_ahead_behind("## main") is None


def test_git_missing_on_adapter_exits_nonzero(tmp_path: Path) -> None:
    _adapter_markers(tmp_path)
    report = run_check(tmp_path, git_exe=None, home=tmp_path / "home")
    assert report.mode == "adapter"
    assert report.exit_code == 1
    assert report.has_prompt("INSTALL_GIT", "todo")
    text = format_report(report)
    assert "PROMPTS" in text
    assert "ADAPTER_NOT_SCIENCE" in text


def test_git_missing_on_plain_folder_exits_nonzero(tmp_path: Path) -> None:
    report = run_check(tmp_path, git_exe=None, home=tmp_path / "home")
    assert report.mode == "unknown"
    assert report.exit_code == 1
    assert report.has_prompt("INSTALL_GIT", "todo")
    assert report.has_prompt("GIT_INIT", "todo")
    _assert_no_publish_prompts(format_report(report))


def test_not_a_git_repo_prompts_git_init(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    report = run_check(tmp_path, home=tmp_path / "home")
    assert report.is_work_tree is False
    assert report.exit_code == 0
    assert report.has_prompt("GIT_INIT", "todo")
    assert not report.has_prompt("CLONE_OR_OVERLAY")
    text = format_report(report)
    assert "git init" in text
    assert "github.com/jymtop/wisp-cursor-bridge" in text
    _assert_no_publish_prompts(text)


def test_after_git_init_recognized_as_initialized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    repo = tmp_path / "folder"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    report = run_check(repo, home=tmp_path / "home")
    assert report.is_work_tree is True
    assert report.exit_code == 0
    assert report.has_prompt("GIT_INITIALIZED", "ok")
    text = format_report(report)
    assert "已 git init" in text
    assert "rollback" in text.lower()
    _assert_no_publish_prompts(text)


def test_initialized_repo_without_remote_is_ok(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "topic")
    report = run_check(repo, home=tmp_path / "home")
    assert report.is_work_tree is True
    assert report.has_prompt("GIT_INITIALIZED", "ok")
    assert report.origin is None
    text = format_report(report)
    _assert_no_publish_prompts(text)
    assert not any("origin" in item.lower() for item in report.warnings)


def test_adapter_mode_by_remote(tmp_path: Path) -> None:
    repo = _init_repo(
        tmp_path / "bridge",
        remote="https://github.com/jymtop/wisp-cursor-bridge.git",
    )
    report = run_check(repo, home=tmp_path / "home")
    assert report.mode == "adapter"
    assert report.is_adapter is True
    assert report.exit_code == 0
    assert report.has_prompt("ADAPTER_NOT_SCIENCE")
    assert report.has_prompt("APPROVE_MCP", "todo")
    assert report.has_prompt("GIT_INITIALIZED", "ok")
    text = format_report(report)
    assert "topic folder" in text
    _assert_no_publish_prompts(text)


def test_adapter_mode_by_files_without_matching_remote(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "local-adapter", remote="https://example.com/scratch.git")
    _adapter_markers(repo)
    report = run_check(repo, home=tmp_path / "home")
    assert report.mode == "adapter"
    assert report.facts["adapter_by_files"] == "yes"
    assert report.has_prompt("ADAPTER_UV_SYNC_OK")


def test_adapter_mode_fork_remote(tmp_path: Path) -> None:
    repo = _init_repo(
        tmp_path / "fork",
        remote="git@github.com:someone/wisp-cursor-bridge.git",
    )
    report = run_check(repo, home=tmp_path / "home")
    assert report.mode == "adapter"
    assert is_bridge_remote(report.origin)


def test_topic_mode_missing_overlay(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "topic", remote="https://github.com/example/my-paper.git")
    report = run_check(repo, home=tmp_path / "home")
    assert report.mode == "topic"
    assert report.exit_code == 0
    assert report.has_prompt("RUN_OVERLAY", "todo")
    text = format_report(report)
    assert "sync_wisp_skills --science" in text
    assert "Never `uv sync`" in text
    assert "pyproject.toml" in text


def test_topic_mode_overlay_present(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "topic", remote="https://github.com/example/my-paper.git")
    mcp = repo / ".cursor" / "mcp.json"
    mcp.parent.mkdir(parents=True)
    mcp.write_text(json.dumps({"mcpServers": {"wisp-bio": {"command": "uv"}}}), encoding="utf-8")
    report = run_check(repo, home=tmp_path / "home")
    assert report.mode == "topic"
    assert report.has_prompt("RUN_OVERLAY", "ok")
    assert report.facts["overlay_wisp_bio"] == "yes"


def test_topic_accidental_pyproject_warns(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "topic", remote="https://github.com/example/my-paper.git")
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "wisp-cursor-bridge"\n',
        encoding="utf-8",
    )
    report = run_check(repo, home=tmp_path / "home")
    assert report.mode == "topic"
    assert any("pyproject.toml" in item for item in report.warnings)
    assert pyproject_looks_accidental(repo / "pyproject.toml")


def test_topics_root_from_env_and_local_file(tmp_path: Path) -> None:
    topics = tmp_path / "topics"
    repo = _init_repo(topics / "paper", remote="https://github.com/example/my-paper.git")
    env_root = read_topics_root(repo, {"WISP_TOPICS_ROOT": str(topics)})
    assert env_root == topics.resolve()

    other = tmp_path / "other-topic"
    other.mkdir()
    local_dir = other / ".wisp"
    local_dir.mkdir()
    (local_dir / "topics-root.local").write_text(f"{topics}\n", encoding="utf-8")
    from_file = read_topics_root(other, {})
    assert from_file == topics.resolve()

    report = run_check(repo, environ={"WISP_TOPICS_ROOT": str(topics)}, home=tmp_path / "home")
    assert report.facts["under_topics_root"] == "yes"
    assert report.has_prompt("PATH_TRIGGER", "info")


def test_detached_head_warns(tmp_path: Path) -> None:
    repo = _init_repo(
        tmp_path / "bridge",
        remote="https://github.com/jymtop/wisp-cursor-bridge.git",
    )
    _git(repo, "checkout", "--detach")
    report = run_check(repo, home=tmp_path / "home")
    assert report.mode == "adapter"
    assert any("Detached HEAD" in item for item in report.warnings)


def test_looks_like_adapter_requires_all_markers(tmp_path: Path) -> None:
    (tmp_path / "INTEROP.md").write_text("# x\n", encoding="utf-8")
    assert looks_like_adapter(tmp_path) is False
    _adapter_markers(tmp_path)
    assert looks_like_adapter(tmp_path) is True


def test_never_reads_live_sqlite(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "topic", remote="https://github.com/example/my-paper.git")
    sqlite = repo / ".wisp" / "wisp.sqlite"
    sqlite.parent.mkdir(parents=True)
    sqlite.write_text("not-a-real-db", encoding="utf-8")
    report = run_check(repo, home=tmp_path / "home")
    assert report.mode == "topic"
    assert sqlite.read_text(encoding="utf-8") == "not-a-real-db"


@pytest.mark.parametrize(
    "status, expected",
    [
        ("## main...origin/main [behind 5]", (0, 5)),
        ("## main...origin/main [ahead 2]", (2, 0)),
    ],
)
def test_parse_ahead_behind_param(status: str, expected: tuple[int, int]) -> None:
    assert parse_ahead_behind(status) == expected
