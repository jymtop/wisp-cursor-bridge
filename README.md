# Wisp × Cursor research bridge

<div align="center">

[English](README.md) · [简体中文](README_zh.md)

</div>

Cursor-side adapter for [Wisp Science](https://github.com/xuzhougeng/wisp-science).
Cursor membership models stay in Cursor. Wisp workflows (skills + bio MCP) run
through this bridge. Scientific state lives on disk as `wisp.handoff.v1`
([INTEROP.md](INTEROP.md)). **Chats do not sync** between the two apps.

Open the **Wisp topic folder** in Cursor — not this adapter repository.

- Skill routing: [research/SKILL-CATALOG.md](research/SKILL-CATALOG.md)
- Current status: [research/HANDOFF.md](research/HANDOFF.md)

This repo does **not** turn a Cursor membership into a Wisp HTTP API key, and
it does not embed the Wisp desktop app.

## Continue a WS task from Cursor

**Path trigger.** If the Cursor workspace is under the Wisp topics root
(example: `D:\AI4S_WispScience\`), it auto-qualifies as a Wisp Science (WS)
topic folder. This adapter repo never qualifies as a science folder.

**Spoken triggers** (also work outside that root):

- 继续 / 接管 / 接上 + WS / Wisp + 任务 / 桥
- 这是WS任务，帮我…
- 读HANDOFF继续
- English: `continue the WS task`, `use the wisp-cursor bridge here`,
  `take over this WS task`, `read HANDOFF and continue`

A Cursor user rule should point at `~/.cursor/skills/ws-continue/SKILL.md`.

**Overlay** the topic folder (run from anywhere; Python 3.12). Never run
`uv sync` in a science folder. `uv sync --python 3.12` belongs **only** in
this adapter repo.

```powershell
uv run --directory <adapter-repo> --python 3.12 python -m tools.sync_wisp_skills --science <topic-folder>
```

`--user-mcp` is optional and needed at most once, and only if this machine
has no user-level MCP yet.

After the first overlay, reload the Cursor window and approve `wisp-bio`,
`wisp-history`, and `figure-library` if they stay grey.

**Back in Wisp:** open the same topic folder and say `读 HANDOFF 继续`.

## Setup (Python 3.12)

Run these only in this adapter repository:

```powershell
uv sync --python 3.12
uv run --python 3.12 pytest
uv run --python 3.12 python -m tools.sync_wisp_skills
```

Live database calls (PubMed, GEO, …) need environment `WISP_BIO_LIVE=1` on the
`wisp-bio` server. License-gated tools (KEGG, CADD, PanglaoDB, Cell Model
Passports) stay off.

## Daily use

1. Open the **same Wisp topic folder** in Wisp and in Cursor (not this adapter).
2. In Cursor, use the path or spoken trigger above, or `/wisp-handoff`.
   Science work should use Wisp skills plus `search_bio_tools` / `use_bio_tool`.
3. Write results to files. Update `research/HANDOFF.md` (`last_app: cursor`).
4. In Wisp: `读 HANDOFF 继续`. Kernel variables do not carry over; rerun
   `research/scripts/`.

Later Wisp plugins: install them in Wisp, then rerun
`python -m tools.sync_wisp_skills`.

## Layout

| Path | Who |
| --- | --- |
| `research/`, `.wisp/WISP.md`, `.wisp/memory/` | Shared (`wisp.handoff.v1`) |
| `.cursor/`, `gateway/`, `tools/` | Cursor only |
| `gateway/` | `wisp-bio` (3-tool MCP over ~247 bio-tools) and read-only `wisp-history` |
| `tools/sync_wisp_skills.py` | Mirrors Wisp / plugin `SKILL.md` into `.cursor/skills/` |
| `vendor/wisp-science/` | Pinned Apache-2.0 skills + bio-tools |

## License

Adapter code is Apache-2.0. Vendored `skills/` and `mcp-servers/bio-tools/`
come from Wisp Science (Apache-2.0 asset bundle). The Wisp desktop application
is AGPL-3.0 and is not vendored. See [NOTICE](NOTICE).
