import json
from pathlib import Path

from tools.sync_wisp_skills import _plugin_mcp_servers, sync_skills


def test_sync_copies_plugin_skill_and_skips_adapter(tmp_path: Path) -> None:
    plugin = tmp_path / "plugin" / "demo-skill"
    plugin.mkdir(parents=True)
    (plugin / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: demo\n---\n# Demo\n",
        encoding="utf-8",
    )
    (plugin / "references").mkdir()
    (plugin / "references" / "note.md").write_text("ref", encoding="utf-8")

    dest = tmp_path / ".cursor" / "skills" / "literature-review"
    dest.mkdir(parents=True)
    (dest / "SKILL.md").write_text(
        "---\nname: literature-review\n---\n<!-- wisp-cursor-adapter: true -->\n# keep\n",
        encoding="utf-8",
    )

    copied = sync_skills(tmp_path, extra_plugin_root=tmp_path / "plugin")
    assert "demo-skill" in copied
    assert (tmp_path / ".cursor" / "skills" / "demo-skill" / "SKILL.md").is_file()
    assert (tmp_path / ".cursor" / "skills" / "demo-skill" / "references" / "note.md").is_file()
    assert "keep" in (dest / "SKILL.md").read_text(encoding="utf-8")


def test_plugin_mcp_expands_wisp_plugin_root(tmp_path: Path) -> None:
    root = tmp_path / "plug" / "demo" / "1.0.0"
    (root / ".wisp-plugin").mkdir(parents=True)
    (root / ".wisp-plugin" / "plugin.json").write_text(
        json.dumps(
            {
                "id": "demo",
                "mcp_servers": [
                    {
                        "id": "demo",
                        "command": "node",
                        "args": ["${WISP_PLUGIN_ROOT}/dist/index.js"],
                        "cwd": ".",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    servers = _plugin_mcp_servers(tmp_path / "plug", system=False)
    assert servers["demo"]["command"] == "node"
    assert servers["demo"]["args"][0].endswith("dist/index.js")
    assert servers["demo"]["env"]["WISP_PLUGIN_ROOT"] == str(root)
    assert servers["demo"]["cwd"] == str(root)
