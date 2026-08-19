import sqlite3
from pathlib import Path

from gateway.wisp_history import get_wisp_transcript, list_wisp_artifacts, list_wisp_sessions
from tests.conftest import invoke


def _make_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE frames (
            id TEXT PRIMARY KEY,
            parent_frame_id TEXT,
            root_frame_id TEXT,
            agent_name TEXT NOT NULL,
            status TEXT NOT NULL,
            project_id TEXT,
            model TEXT,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        );
        CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            frame_id TEXT NOT NULL,
            seq INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT,
            ts INTEGER NOT NULL
        );
        CREATE TABLE artifacts (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            root_frame_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            storage_path TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        """
    )
    conn.execute(
        "INSERT INTO frames VALUES (?,?,?,?,?,?,?,?,?)",
        ("frm-1", None, None, "wisp", "complete", "p1", "demo", 1, 2),
    )
    conn.execute(
        "INSERT INTO messages VALUES (?,?,?,?,?,?)",
        ("m1", "frm-1", 1, "user", "Continue TP53 QC", 1),
    )
    conn.execute(
        "INSERT INTO messages VALUES (?,?,?,?,?,?)",
        ("m2", "frm-1", 2, "assistant", "HANDOFF next is PubMed PMIDs", 2),
    )
    conn.execute(
        "INSERT INTO artifacts VALUES (?,?,?,?,?,?,?)",
        ("a1", "p1", "frm-1", "umap.png", "image/png", "research/figures/umap.png", 3),
    )
    conn.commit()
    conn.close()


def test_history_lists_frame_and_transcript(tmp_path: Path) -> None:
    db = tmp_path / ".wisp" / "wisp.sqlite"
    _make_db(db)
    root = str(tmp_path)
    listed = invoke(list_wisp_sessions, root)
    assert "frm-1" in listed
    text = invoke(get_wisp_transcript, "frm-1", root)
    assert "Continue TP53 QC" in text
    arts = invoke(list_wisp_artifacts, root)
    assert "umap.png" in arts


def test_history_missing_db(tmp_path: Path) -> None:
    assert "no sqlite" in invoke(list_wisp_sessions, str(tmp_path))


def test_history_respects_wisp_sqlite_env(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "app" / "wisp.sqlite"
    _make_db(db)
    empty = tmp_path / "empty-project"
    empty.mkdir()
    monkeypatch.setenv("WISP_SQLITE", str(db))
    listed = invoke(list_wisp_sessions, str(empty))
    assert "frm-1" in listed
