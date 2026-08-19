from gateway.bio_catalog import load_catalog
from gateway.wisp_bio_gateway import search_bio_tools, use_bio_tool
from tests.conftest import invoke


def test_pubmed_search_finds_search_articles() -> None:
    catalog = load_catalog()
    hits = catalog.search("pubmed search")
    names = {tool for _, tool in hits}
    assert "search_articles" in names


def test_deferred_kegg_not_listed() -> None:
    catalog = load_catalog()
    names = {tool for _, tool in catalog.all_tools()}
    assert "search_kegg" not in names
    assert "cadd_variant_score" not in names
    assert "panglaodb_marker_genes" not in names


def test_search_tool_json() -> None:
    payload = invoke(search_bio_tools, "pubmed")
    assert "search_articles" in payload


def test_use_tool_live_disabled_and_deferred() -> None:
    live = invoke(use_bio_tool, "search_articles", "{}")
    assert "live_disabled" in live
    deferred = invoke(use_bio_tool, "search_kegg", "{}")
    assert "deferred_license" in deferred
