# Repository Guidelines

Cursor-side adapter for [Wisp Science](https://github.com/xuzhougeng/wisp-science). Shared research state follows `wisp.handoff.v1` in [INTEROP.md](INTEROP.md). Route tasks with [research/SKILL-CATALOG.md](research/SKILL-CATALOG.md).

## First open / clone

Once per session run `uv run --python 3.12 python -m tools.check_bridge_setup` (or read `tools/check_bridge_setup.py`). If this workspace is the adapter (`origin` ends with `wisp-cursor-bridge`, or `INTEROP.md` + `gateway/` + `tools/sync_wisp_skills.py`), show the script’s prompt list — do **not** treat it as a science topic. If it is a topic folder without `wisp-bio` in `.cursor/mcp.json`, prompt:

`uv run --directory <adapter-repo> --python 3.12 python -m tools.sync_wisp_skills --science <this-folder>`

then Reload Window. Never `uv sync` or add `pyproject.toml` in a topic folder. Do not pass `--user-mcp` unless `~/.cursor/mcp.json` has no `wisp-bio`.

**Triggers** (also `.cursor/rules/wisp-bridge.mdc` and `/ws-continue`): 继续这个WS任务, 接管WS任务, 接上Wisp桥, 读HANDOFF继续, 这是WS任务，帮我…, 从Wisp转过来, 用Cursor接着做, `continue the WS task`, `wire the wisp bridge`. Pattern: (WS|Wisp|wisp|维斯普) AND (继续|接管|接上|接着|交接|HANDOFF|帮我|我要|帮忙|桥|课题) OR starts with 这是WS / 这是Wisp / WS任务 / Wisp任务. Optional path: workspace under `WISP_TOPICS_ROOT` or `.wisp/topics-root.local`.

## Project Structure & Module Organization

- `gateway/` — `wisp-bio` (3-tool MCP over ~247 bio-tools) and read-only `wisp-history`.
- `tools/sync_wisp_skills.py` — mirrors Wisp / plugin `SKILL.md` into `.cursor/skills/`.
- `tools/check_bridge_setup.py` — git + overlay prompt list for new clones.
- `vendor/wisp-science/` — pinned sparse snapshot (`mcp-servers/bio-tools`, `skills`).
- `research/` — HANDOFF, sessions, scripts (Python 3.12). `.wisp/` — `WISP.md` and `memory/`.
- `.cursor/` — MCP, adapted skills, router + bridge rules. Cursor-only; not INTEROP.

## Build, Test, and Development Commands

```powershell
uv sync --python 3.12
uv run --python 3.12 pytest
uv run --python 3.12 python -m tools.check_bridge_setup
uv run --python 3.12 python -m tools.sync_wisp_skills --science "<topic-folder>"
```

`uv sync` belongs **only** in this adapter. Then approve `wisp-bio`, `wisp-history`, and `figure-library`. Live bio calls need `WISP_BIO_LIVE=1`.

## Coding Style & Naming Conventions

4-space indent, type hints, `snake_case` modules. Do not invent PMIDs/DOIs. Do not enable KEGG/CADD/PanglaoDB/Cell Model Passports.

## Testing Guidelines

`tests/test_*.py` via pytest. History tests use a fixture sqlite, never a real `.wisp/wisp.sqlite`. Setup-check tests use `tmp_path` + `git init`.

## Commit & Pull Request Guidelines

Conventional, why-focused messages (`add bio gateway so Cursor can search PubMed`). PRs: summary, INTEROP impact, pytest. No secrets, no live `wisp.sqlite`, no private letters under `docs/`.

## Agent-Specific Instructions

Start: setup check (once) + `research/HANDOFF.md`. Science → Wisp skills + `search_bio_tools`/`use_bio_tool`. Git/PR/refactor this repo → Cursor skills. End: update HANDOFF (`last_app: cursor`), write `research/sessions/cursor-*.md`, short facts in `.wisp/memory/`. Delete files with `.Trash` + `mv`, not `rm`.
