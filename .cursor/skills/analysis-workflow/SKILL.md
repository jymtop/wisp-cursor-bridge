---
name: analysis-workflow
description: Organize multi-step scientific analyses into reproducible modules (QC, PCA, DEG, GSEA). Use when a stage produces scripts, figures, tables, and methods.
license: Apache-2.0
---
<!-- wisp-cursor-adapter: true -->

# Analysis workflow (Cursor adapter)

Adapted from Wisp `analysis-workflow`. Use Cursor file and terminal tools. Python 3.12.

## Layout

```text
<module>/
  scripts/
  input/
  output/figures/
  output/tables/
  README.md
```

Or, for this adapter's default project, put small jobs in `research/scripts/` and figures in `research/figures/`.

## Rules

- One producing script per output. Record versions actually used.
- Do not duplicate large raw data. Reference `raw/` or `data/`.
- Verify outputs exist before claiming done.
- Update module README or `research/notes/` methods from executed code.
- End with `/wisp-handoff` write-back.
