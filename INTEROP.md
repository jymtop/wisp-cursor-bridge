# wisp.handoff.v1

Stable project-folder contract for Wisp Science and other clients (Cursor is
the first). This file is what upstream Wisp can adopt. It does **not** mention
`.cursor/` paths.

Upstream Wisp already reads `AGENTS.md` and `.wisp/WISP.md`, and can search
`.wisp/memory/*.md`. Today a user can say “read HANDOFF and continue” with no
Wisp code change. Official support is auto-inject + auto-write-back.

## Shared paths

| Path | Role |
| --- | --- |
| `research/HANDOFF.md` | Current status. One file. Last writer wins. |
| `research/sessions/{app}-{YYYY-MM-DD}-{slug}.md` | Chunk notes. `app` is `wisp`, `cursor`, or another client. |
| `research/scripts/` | Rerunnable analysis (Python 3.12 unless the project says otherwise). |
| `research/figures/` | Figures referenced from HANDOFF. |
| `research/notes/` | Tables, PMID lists, lab notes. |
| `.wisp/memory/*.md` | Short durable facts for Wisp `search_memory`. |
| `AGENTS.md` | Client-neutral project instructions. |
| `.wisp/WISP.md` | Wisp-preferred overlay; must not contradict HANDOFF rules. |

Skill public names should stay aligned with Wisp bundled skills
(`literature-review`, `analysis-workflow`, `singlecell-qc`, `pdf-explore`,
`public-data-access`, `figure-composer`, `paper-narrative`, `local-env-setup`).

## `research/HANDOFF.md` fields

Required list items:

- `last_app` — `wisp` \| `cursor` \| other lowercase id
- `last_at` — local time `YYYY-MM-DD HH:MM`
- `status` — `in_progress` \| `blocked` \| `done`
- `question` — one-line research question
- `next` — the single next action
- `key_files` — project-relative paths
- `open_questions` — unresolved scientific questions
- `do_not` — hard constraints (do not touch `raw/`, …)

Example:

```markdown
# HANDOFF

- last_app: cursor
- last_at: 2026-08-19 11:40
- status: in_progress
- question: TP53 reviews plus local QC
- next: add 5 PMIDs to research/notes/pmid.tsv
- key_files:
  - research/scripts/qc_pbmc.py
- open_questions:
  - exclude doublets?
- do_not:
  - do not modify raw/
```

## Session note

Minimum sections: Goal, Done, Outputs, Open. Outputs are paths, not chat
quotes.

## Memory notes

One fact per file when possible (`QC_THRESHOLD=0.047`). No full transcripts.

## Client rules

1. Start: read HANDOFF, latest session note, relevant memory.
2. Work: write rerunnable files; do not leave results only in chat.
3. End: update HANDOFF, write a session note, write memory facts.
4. Chat bubbles are not part of this contract.

## Suggested Wisp PR (for upstream)

1. If `research/HANDOFF.md` exists, inject it on new session (same as `AGENTS.md`).
2. On `/handoff` or turn end: rewrite HANDOFF, write `research/sessions/wisp-*.md`,
   append important facts to `.wisp/memory/`.
3. Optional: list `research/sessions/cursor-*.md` like Codex/Claude import.
4. Keep bundled skill names stable; cite this spec as `wisp.handoff.v1`.
