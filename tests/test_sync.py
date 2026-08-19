from pathlib import Path

from tools.sync_wisp_skills import sync_skills


def test_sync_copies_plugin_skill_and_skips_adapter(tmp_path: Path) -> None:
    plugin = tmp_path / "plugin" / "demo-skill"
    plugin.mkdir(parents=True)
    (plugin / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: demo\n---\n# Demo\n",
        encoding="utf-8",
    )

    dest = tmp_path / ".cursor" / "skills" / "literature-review"
    dest.mkdir(parents=True)
    (dest / "SKILL.md").write_text(
        "---\nname: literature-review\n---\n<!-- wisp-cursor-adapter: true -->\n# keep\n",
        encoding="utf-8",
    )

    copied = sync_skills(tmp_path, extra_plugin_root=tmp_path / "plugin")
    assert "demo-skill" in copied
    assert (tmp_path / ".cursor" / "skills" / "demo-skill" / "SKILL.md").is_file()
    assert "keep" in (dest / "SKILL.md").read_text(encoding="utf-8")
