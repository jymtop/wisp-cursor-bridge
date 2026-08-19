---
name: wisp-handoff
description: Read and update wisp.handoff.v1. Use at the start or end of a research chunk, or when switching between Wisp and Cursor.
---
<!-- wisp-cursor-adapter: true -->

# Wisp handoff

Follow [INTEROP.md](../../../INTEROP.md).

## Start

1. Read `research/HANDOFF.md`.
2. Read the newest `research/sessions/*.md`.
3. Read relevant `.wisp/memory/*.md`.
4. Do the single `next` item. Do not expand scope.

## End

1. Set `last_app` to `cursor` (or `wisp` if you are documenting a Wisp turn).
2. Set `last_at`, `next`, `key_files`.
3. Write `research/sessions/cursor-YYYY-MM-DD-topic.md` (Goal / Done / Outputs / Open).
4. Write short facts to `.wisp/memory/`.
5. Leave rerunnable scripts under `research/scripts/` (Python 3.12).
