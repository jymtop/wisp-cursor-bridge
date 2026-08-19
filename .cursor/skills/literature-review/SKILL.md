---
name: literature-review
description: Retrieve and synthesize scientific literature. Use for papers, evidence summaries, method comparisons, and gap analyses. Every citation must come from a live lookup via wisp-bio, never from memory.
license: Apache-2.0
---
<!-- wisp-cursor-adapter: true -->

# Literature review (Cursor adapter)

Adapted from Wisp `literature-review` (Apache-2.0). Do not call Wisp `use_skill`.

## Tools

1. `search_bio_tools` with query `pubmed` or `openalex`.
2. `use_bio_tool` for `search_articles`, `get_article_metadata`, `openalex_search_works`, or `openalex_get_work`.
3. Set `WISP_BIO_LIVE=1` in the MCP env when a real network call is required.

Never invent a DOI, PMID, or retraction status. Cite as `[Author Year](https://doi.org/...)`.

## Steps

Scope → sweep (live) → expand citations if tools allow → verify IDs → write by theme → save Markdown under `research/notes/` and update HANDOFF.

Save the review path in `key_files`. Do not dump process narration into the paper.
