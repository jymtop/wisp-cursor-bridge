from pathlib import Path

from gateway.handoff import continue_from_wisp, parse_handoff


SAMPLE = """# HANDOFF

- last_app: wisp
- last_at: 2026-08-19 10:15
- status: in_progress
- question: TP53
- next: add PMIDs
- key_files:
  - research/scripts/qc_pbmc.py
- open_questions:
  - doublets?
- do_not:
  - do not modify raw/
"""


def test_parse_handoff() -> None:
    data = parse_handoff(SAMPLE)
    assert data.last_app == "wisp"
    assert data.key_files == ["research/scripts/qc_pbmc.py"]
    assert data.do_not == ["do not modify raw/"]


def test_cursor_can_continue_wisp_handoff(tmp_path: Path) -> None:
    path = tmp_path / "research" / "HANDOFF.md"
    path.parent.mkdir(parents=True)
    path.write_text(SAMPLE, encoding="utf-8")
    updated = continue_from_wisp(
        path,
        next_step="run research/scripts/qc_pbmc.py on the real h5ad",
        key_files=["research/notes/pmid.tsv"],
        last_app="cursor",
    )
    text = path.read_text(encoding="utf-8")
    assert updated.last_app == "cursor"
    assert "pmid.tsv" in text
    assert "qc_pbmc.py" in text
    assert "run research/scripts/qc_pbmc.py" in text
