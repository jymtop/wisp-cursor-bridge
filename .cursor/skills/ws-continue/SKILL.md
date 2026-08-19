---
name: ws-continue
description: >
  Wire the Wisp-Cursor bridge into the CURRENT workspace and continue from
  research/HANDOFF.md. Path wins: WHEN the Cursor workspace root or cwd is
  under D:\AI4S_WispScience\ or D:/AI4S_WispScience/ (case-insensitive
  ai4s_wispscience), treat it as a Wisp Science (WS) topic folder and run this
  skill on the first relevant turn — no spoken passphrase required. Never treat
  D:\Cursor-task\WispScienceCursor化 as a science folder. ALSO WHEN the user
  says any of: 继续这个WS任务, 继续WS任务, 继续这个 Wisp 任务, 继续这个wisp任务,
  继续wisp任务, 继续 Wisp 任务, 接管这个WS任务, 接管WS任务, 接管这个Wisp任务,
  接管wisp任务, 接上这个WS任务, 接上WS任务, 接上Wisp桥, 接上这个桥, 把桥接上,
  接上桥, 读HANDOFF继续, 读 HANDOFF 继续, 读handoff继续, 读交接继续,
  这是WS任务, 这是 WS 任务, 这是Wisp任务, 这是 Wisp 任务, 这是wisp任务,
  这是WS任务，帮我, 这是WS任务，请帮我, 这是WS任务，我要, 这是WS任务，帮忙,
  这是Wisp任务，帮我, 这是Wisp任务，请帮我, 这是Wisp任务，我要,
  WS任务，帮我, WS任务，请帮我, WS任务，我要,
  Wisp任务，帮我, Wisp任务，请帮我, Wisp任务，我要,
  在Cursor继续WS, 在 Cursor 继续, 从Wisp转过来, 从 WS 转过来,
  用Cursor接着做, 用 Cursor 接着做, 接着做这个WS, 接着做WS,
  回到这个WS课题, 打开WS课题继续,
  use the wisp-cursor bridge here, continue the WS task, continue this Wisp task,
  wire the wisp bridge, take over this WS task; or any sentence that starts with
  or contains 这是WS任务 / 这是 WS 任务 / 这是Wisp任务 / 这是wisp任务 /
  WS任务 / Wisp任务 followed by 帮我 / 请帮我 / 我要 / 帮忙; or the message
  contains (WS or Wisp or wisp or 维斯普) AND any of 继续/接管/接上/接着/交接/
  HANDOFF/handoff/帮我/请帮我/我要/帮忙/桥/课题; or starts with 这是WS / 这是 WS /
  这是Wisp / 这是wisp / WS任务 / Wisp任务; or any close variant with
  继续/接管/接上 + WS/Wisp/wisp + 任务/桥. Spoken phrases still fire even if
  the folder is NOT under the Wisp topics root.
  After wiring, do the user's xxx (the rest of the sentence), not only HANDOFF
  next, if they already specified work. Use to resume a WS task in a bare topic
  folder that may not have project .cursor/rules yet.
---
<!-- wisp-cursor-adapter: true -->

# WS continue — wire bridge + HANDOFF

Personal auto-invoke skill. Works before project `.cursor/rules` exist.

**Path wins.** A workspace under `D:\AI4S_WispScience\` is a WS topic folder
even with no passphrase. Spoken passphrases still fire in any other folder.

## Triggers

### Path (highest priority — no passphrase)

If the Cursor workspace root or `cwd` is under any of:

- `D:\AI4S_WispScience\`
- `D:/AI4S_WispScience/`
- case-insensitive `ai4s_wispscience`

then this **is** a Wisp Science (WS) topic folder. On the **first relevant
turn** in that workspace (new chat, or user starts work), run this skill.

Do **not** treat `D:\Cursor-task\WispScienceCursor化` as a science folder
even if someone mentions Wisp.

### Continue / take over

继续这个WS任务 · 继续WS任务 · 继续这个 Wisp 任务 · 继续这个wisp任务 ·
继续wisp任务 · 继续 Wisp 任务 ·
接管这个WS任务 · 接管WS任务 · 接管这个Wisp任务 · 接管wisp任务 ·
接上这个WS任务 · 接上WS任务 · 接上Wisp桥 · 接上这个桥 · 把桥接上 · 接上桥 ·
读HANDOFF继续 · 读 HANDOFF 继续 · 读handoff继续 · 读交接继续

### This is a WS task + request

这是WS任务 · 这是 WS 任务 · 这是Wisp任务 · 这是 Wisp 任务 · 这是wisp任务 ·
这是WS任务，帮我… / 请帮我… / 我要… / 帮忙… ·
这是Wisp任务，帮我… / 请帮我… / 我要… ·
WS任务，帮我… / 请帮我… / 我要… ·
Wisp任务，帮我… / 请帮我… / 我要…

### Resume / switch apps

在Cursor继续WS · 在 Cursor 继续 · 从Wisp转过来 · 从 WS 转过来 ·
用Cursor接着做 · 用 Cursor 接着做 · 接着做这个WS · 接着做WS ·
回到这个WS课题 · 打开WS课题继续

### English

use the wisp-cursor bridge here · continue the WS task · continue this Wisp task ·
wire the wisp bridge · take over this WS task

### Phrase pattern (fire if)

Message contains (WS or Wisp or wisp or 维斯普) AND any of:
继续, 接管, 接上, 接着, 交接, HANDOFF, handoff, 帮我, 请帮我, 我要, 帮忙, 桥, 课题

OR the message starts with 这是WS / 这是 WS / 这是Wisp / 这是wisp / WS任务 / Wisp任务.

Spoken families still work if the folder is **not** under the Wisp topics
root (example: `D:\AI4S_WispScience\`).

## 1. Detect workspace (path check first)

Workspace root = Cursor project root (`cwd`). Check path **once per session**.

1. If the folder **is** `D:\Cursor-task\WispScienceCursor化`, this **is** the
   bridge adapter — not a science folder. Tell the user to open a Wisp topic
   folder and do science there. Stop.
2. If the workspace root or cwd is under `D:\AI4S_WispScience\` /
   `D:/AI4S_WispScience/` / case-insensitive `ai4s_wispscience`, this **is** a
   WS topic folder. Continue (no passphrase required).
3. If a spoken passphrase / phrase pattern matched, continue even when the
   path is elsewhere.

## 2. Install overlay if needed (once per session)

If `.cursor\mcp.json` is missing **or** does not contain `wisp-bio`, run in
PowerShell (Python 3.12). Do **not** run `uv sync` in the science folder.
Do **not** add `pyproject.toml` there. Do **not** pass `--user-mcp`
(user MCP already exists).

Do **not** re-run sync on every later message if the overlay is already
present — only check path + `mcp.json` once per session.

```powershell
uv run --directory "<adapter-repo>" --python 3.12 python -m tools.sync_wisp_skills --science "<WORKSPACE_ROOT>"
```

Replace `<adapter-repo>` with this clone and `<WORKSPACE_ROOT>` with the
workspace absolute path. Do not pass `--user-mcp` unless this machine has
no user MCP yet.

## 3. Ensure `research\HANDOFF.md`

If missing, create a minimal `wisp.handoff.v1` file (`last_app: cursor`).
Take `question` / `next` from existing `handoff.md`, `AGENTS.md`, or the newest
report if any. Do not invent PMIDs or DOIs. Do not modify `data/raw/`.

## 4. Continue: user's xxx or HANDOFF next

Read `research/HANDOFF.md`, newest `research/sessions/*`, and `.wisp/memory/`
if present (context only). After wiring:

- If the user already specified work (xxx after 帮我 / 请帮我 / 我要 / 帮忙,
  or the rest of the sentence), do that xxx. Do not only do HANDOFF `next`.
- If they only said a trigger with no xxx, or the path auto-fired with no
  extra task, do the single HANDOFF `next` item.

Then update HANDOFF and write a session note.

## 5. After first overlay

Tell the user they may need **Reload Window** once so project skills/MCP appear.
If MCP stays grey, approve `wisp-bio` / `wisp-history` / `figure-library`.
