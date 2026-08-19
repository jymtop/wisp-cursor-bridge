# Repository Guidelines

Cursor-side adapter for [Wisp Science](https://github.com/xuzhougeng/wisp-science). Shared research state follows `wisp.handoff.v1` in [INTEROP.md](INTEROP.md). Route tasks with [research/SKILL-CATALOG.md](research/SKILL-CATALOG.md).

## Project Structure & Module Organization

- `gateway/` — `wisp-bio` (3-tool MCP over ~247 bio-tools) and read-only `wisp-history`.
- `tools/sync_wisp_skills.py` — mirrors Wisp / plugin `SKILL.md` into `.cursor/skills/`.
- `vendor/wisp-science/` — pinned sparse snapshot (`mcp-servers/bio-tools`, `skills`).
- `research/` — HANDOFF, sessions, scripts (Python 3.12), figures, notes.
- `.wisp/` — `WISP.md` and `memory/` (Wisp can search these without code changes).
- `.cursor/` — MCP, adapted skills, router rule. Cursor-only; not part of INTEROP.

## Build, Test, and Development Commands

```powershell
uv sync --python 3.12
uv run --python 3.12 pytest
uv run --python 3.12 python -m tools.sync_wisp_skills
```

Overlay a topic folder (Python 3.12). Add `--user-mcp` only if this machine has no user MCP yet:

```powershell
uv run --python 3.12 python -m tools.sync_wisp_skills --science "<topic-folder>"
```

Then approve `wisp-bio`, `wisp-history`, and `figure-library` in Cursor Settings → Tools & MCP. Live bio calls need `WISP_BIO_LIVE=1`.

## Coding Style & Naming Conventions

4-space indent, type hints, `snake_case` modules. Do not invent PMIDs/DOIs. Do not enable KEGG/CADD/PanglaoDB/Cell Model Passports.

## Testing Guidelines

`tests/test_*.py` via pytest. History tests use a fixture sqlite, never a real `.wisp/wisp.sqlite`.

## Commit & Pull Request Guidelines

Conventional, why-focused messages (`add bio gateway so Cursor can search PubMed`). PRs: summary, INTEROP impact, pytest. No secrets, no live `wisp.sqlite`.

## Agent-Specific Instructions

Start: read `research/HANDOFF.md`. Science → Wisp skills + `search_bio_tools`/`use_bio_tool`. Git/PR/refactor this repo → Cursor skills. End: update HANDOFF (`last_app: cursor`), write `research/sessions/cursor-*.md`, short facts in `.wisp/memory/`. Delete files with `.Trash` + `mv`, not `rm`.
