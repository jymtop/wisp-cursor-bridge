from research.scripts.qc_pbmc import summarize


def test_summarize_mentions_no_filter() -> None:
    assert "no filter" in summarize(100, 20)
