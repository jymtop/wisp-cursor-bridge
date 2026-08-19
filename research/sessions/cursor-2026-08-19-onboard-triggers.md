# cursor-2026-08-19-onboard-triggers

## Goal

Package portable WS trigger phrases and a git setup check so people who clone
https://github.com/jymtop/wisp-cursor-bridge get prompted to finish Cursor
settings. No personal User Rules, no machine-specific topic roots, no private
letters, no science-topic names.

## Done

- Single source of truth: `.cursor/rules/wisp-bridge.mdc` (alwaysApply),
  `.cursor/skills/ws-continue/SKILL.md`, `AGENTS.md` First open / clone.
- `tools/check_bridge_setup.py` + `tests/test_check_bridge_setup.py`
  (tmp git repos only).
- README.md / README_zh.md rewritten for other users; optional topics root
  and a short portable User Rule template.
- Overlay now copies `wisp-bridge.mdc` into topic folders.
- `.wisp/topics-root.local` gitignored; example file committed.

## Outputs

- `tools/check_bridge_setup.py`
- `tests/test_check_bridge_setup.py`
- `README.md`, `README_zh.md`, `AGENTS.md`

## Open

New clones still need one Reload Window and MCP approve after the first
overlay.
