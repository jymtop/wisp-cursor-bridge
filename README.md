# Wisp × Cursor research bridge

Cursor-side adapter for [Wisp Science](https://github.com/xuzhougeng/wisp-science).
Use Wisp workflows (skills + bio MCP) with a Cursor membership. Research state
lives on disk as `wisp.handoff.v1` so Wisp can continue after Cursor, and the
other way around.

- Interop spec (give this to Wisp upstream): [INTEROP.md](INTEROP.md)
- Skill routing: [research/SKILL-CATALOG.md](research/SKILL-CATALOG.md)
- Current status: [research/HANDOFF.md](research/HANDOFF.md)

This repo does **not** turn a Cursor membership into a Wisp HTTP API key, and
it does not embed the Wisp desktop app.

## Setup (Python 3.12)

```powershell
uv sync --python 3.12
uv run --python 3.12 pytest
uv run --python 3.12 python -m tools.sync_wisp_skills
```

In Cursor: Settings → Tools & MCP → approve `wisp-bio` and `wisp-history`.

Live database calls (PubMed, GEO, …) need environment `WISP_BIO_LIVE=1` on the
`wisp-bio` server. License-gated tools (KEGG, CADD, PanglaoDB, Cell Model
Passports) stay off.

## Daily use

1. Open the **same project folder** in Wisp and in Cursor.
2. While you still have a Wisp API key: work in Wisp, then update HANDOFF
   (or say “write HANDOFF”).
3. When that key is exhausted: in Cursor say `read HANDOFF and continue`
   or `/wisp-handoff`. Science tasks should hit Wisp skills + `search_bio_tools`.
4. Back in Wisp: `读 HANDOFF，按 next 继续`. Kernel variables do not carry over;
   rerun `research/scripts/`.

Later Wisp plugins: install them in Wisp, then rerun `python -m tools.sync_wisp_skills`.

## Layout

| Path | Who |
| --- | --- |
| `research/`, `.wisp/WISP.md`, `.wisp/memory/` | Shared (`wisp.handoff.v1`) |
| `.cursor/`, `gateway/`, `tools/` | Cursor only |
| `vendor/wisp-science/` | Pinned Apache-2.0 skills + bio-tools |

## License

Adapter code is Apache-2.0. Vendored `skills/` and `mcp-servers/bio-tools/`
come from Wisp Science (Apache-2.0 asset bundle). The Wisp desktop application
is AGPL-3.0 and is not vendored. See [NOTICE](NOTICE).
