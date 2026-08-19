# cursor-2026-08-19-git-init-check

## Goal

Correct the published meaning of “git 检测”: it is whether `git init`
already happened (local work tree), not `git remote` mode switching.
Local git is for history and rollback only.

## Done

- `tools/check_bridge_setup.py` leads with git-installed + work-tree checks.
  No repo → prompt `git init` (or clone the adapter). Already a repo →
  已 git init. Exit 0 unless the git binary is missing.
- Tests: tmp dir without `.git` prompts init; after `git init` it is
  recognized. Missing remote is not a warning. User-facing text never
  asks to push.
- README / AGENTS / rules / ws-continue / bridge-usage.html: adapter vs
  topic is files (`INTEROP.md` + `gateway/` + `tools/sync_wisp_skills.py`).

## Outputs

- `tools/check_bridge_setup.py`
- `tests/test_check_bridge_setup.py`
- `README.md`, `README_zh.md`, `AGENTS.md`
