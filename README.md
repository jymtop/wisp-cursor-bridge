# Wisp × Cursor research bridge

<div align="center">

[English](README.md) · [简体中文](README_zh.md)

</div>

Cursor-side adapter for [Wisp Science](https://github.com/xuzhougeng/wisp-science).
Cursor membership models stay in Cursor. Wisp workflows (skills + bio MCP) run
through this bridge. Scientific state lives on disk as `wisp.handoff.v1`
([INTEROP.md](INTEROP.md)). **Chats do not sync** between the two apps.

This repo does **not** turn a Cursor membership into a Wisp HTTP API key, and
it does not embed the Wisp desktop app.

Open a **Wisp topic folder** in Cursor for science work — not this adapter
repository.

- Skill routing: [research/SKILL-CATALOG.md](research/SKILL-CATALOG.md)
- Current status: [research/HANDOFF.md](research/HANDOFF.md)

## For other users (clone this GitHub URL)

Do **not** paste anyone’s personal Cursor User Rules. Machine-specific paths
are examples only.

1. Clone [https://github.com/jymtop/wisp-cursor-bridge](https://github.com/jymtop/wisp-cursor-bridge).
2. Open **this** folder in Cursor (Claude Code and similar tools read
   [AGENTS.md](AGENTS.md)).
3. On the first relevant turn the agent should run the setup check and
   **prompt you** to finish settings (git, MCP approve, overlay a topic
   folder). You can also run it yourself:

```powershell
uv run --python 3.12 python -m tools.check_bridge_setup
```

The checker prints a prompt list. Adapter mode means you opened the bridge
repo: do science elsewhere; `uv sync --python 3.12` is OK **here only**.
Topic-folder mode means overlay if `.cursor/mcp.json` has no `wisp-bio`.

### Trigger phrases

Say any of these in a topic folder (or a close match to the Pattern). After
a trigger, the agent follows `.cursor/skills/ws-continue/SKILL.md`: overlay
if needed, read `research/HANDOFF.md`, then do your xxx or HANDOFF `next`.

| Family | Phrases |
| --- | --- |
| Continue / take over | 继续这个WS任务, 继续WS任务, 继续这个 Wisp 任务, 接管WS任务, 接上Wisp桥, 读HANDOFF继续, … |
| This is a WS task | 这是WS任务，帮我… / 请帮我… / 我要…; WS任务，帮我… |
| Resume | 从Wisp转过来, 用Cursor接着做, 接着做这个WS |
| English | `use the wisp-cursor bridge here`, `continue the WS task`, `wire the wisp bridge`, `take over this WS task` |
| Pattern | (WS or Wisp or wisp or 维斯普) AND (继续 / 接管 / 接上 / 接着 / 交接 / HANDOFF / 帮我 / 请帮我 / 我要 / 帮忙 / 桥 / 课题), **or** starts with 这是WS / 这是Wisp / WS任务 / Wisp任务 |

Path trigger is **optional**. If you set `WISP_TOPICS_ROOT` or one path line
in `.wisp/topics-root.local` (see `.wisp/topics-root.local.example`), a
workspace under that root auto-qualifies. This adapter never qualifies.

### Overlay a topic folder

```powershell
uv run --directory <adapter-repo> --python 3.12 python -m tools.sync_wisp_skills --science <topic-folder>
```

Never run `uv sync` in a science folder. Never add `pyproject.toml` there.
Do not pass `--user-mcp` unless `~/.cursor/mcp.json` has no `wisp-bio`.
After the first overlay: Reload Window, then approve `wisp-bio`,
`wisp-history`, and `figure-library` if they stay grey.

### Optional short User Rule (portable)

After you copy `.cursor/skills/ws-continue/SKILL.md` to
`~/.cursor/skills/ws-continue/SKILL.md` (or after the first overlay), you
may add a short User Rule. Do not paste someone else’s personal rules.

```
Follow ~/.cursor/skills/ws-continue/SKILL.md (or .cursor/skills/ws-continue/SKILL.md).
If this workspace is under WISP_TOPICS_ROOT or .wisp/topics-root.local, treat it as a WS topic folder.
Never treat a wisp-cursor-bridge clone (INTEROP.md + gateway/ + tools/sync_wisp_skills.py) as a science folder.
Spoken: 继续WS任务, 接上Wisp桥, 读HANDOFF继续, 这是WS任务，帮我…, continue the WS task, wire the wisp bridge.
After a trigger: overlay if needed, read research/HANDOFF.md, do the user's xxx or HANDOFF next.
Never uv sync in a topic folder. Do not pass --user-mcp unless ~/.cursor/mcp.json has no wisp-bio.
```

**Back in Wisp:** open the same topic folder and say `读 HANDOFF 继续`.

## Setup (Python 3.12)

Run these only in this adapter repository:

```powershell
uv sync --python 3.12
uv run --python 3.12 pytest
uv run --python 3.12 python -m tools.check_bridge_setup
uv run --python 3.12 python -m tools.sync_wisp_skills
```

Live database calls (PubMed, GEO, …) need environment `WISP_BIO_LIVE=1` on the
`wisp-bio` server. License-gated tools (KEGG, CADD, PanglaoDB, Cell Model
Passports) stay off.

## Daily use

1. Open the **same Wisp topic folder** in Wisp and in Cursor (not this adapter).
2. In Cursor, use a trigger above, or `/wisp-handoff`. Science work should use
   Wisp skills plus `search_bio_tools` / `use_bio_tool`.
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
| `tools/check_bridge_setup.py` | Git + overlay prompt list for new clones |
| `vendor/wisp-science/` | Pinned Apache-2.0 skills + bio-tools |

## License

Adapter code is Apache-2.0. Vendored `skills/` and `mcp-servers/bio-tools/`
come from Wisp Science (Apache-2.0 asset bundle). The Wisp desktop application
is AGPL-3.0 and is not vendored. See [NOTICE](NOTICE).
