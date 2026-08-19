---
name: public-data-access
description: Find and record public omics accessions (GEO, ArrayExpress, PRIDE, MetaboLights). Use before downloading large datasets.
---
<!-- wisp-cursor-adapter: true -->

# Public data access (Cursor adapter)

1. `search_bio_tools` for `geo`, `arrayexpress`, `pride`, or `metabolights`.
2. `use_bio_tool` only after the user confirms the accession.
3. Record accession, URL, access date, and intended local path in `research/notes/`.
4. Do not download huge archives without asking. Prefer references over copies (`analysis-workflow`).

Update HANDOFF `key_files` with the note path.
