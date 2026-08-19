---
name: singlecell-qc
description: Human-in-the-loop scRNA-seq QC in Python 3.12. Inspect, compute metrics, propose thresholds, wait for approval before filtering or merging.
---
<!-- wisp-cursor-adapter: true -->

# Single-cell QC (Cursor adapter)

Adapted from Wisp `singlecell-qc`. Not a one-click pipeline.

## Loop

inspect → metrics → human review → confirm thresholds → small action → re-inspect

Do not filter, run Scrublet, or merge unless the user explicitly approves.

## First pass

Report matrix type, species, sample count, and the next single step. Ask which samples to pilot.

Write rerunnable scripts under `research/scripts/` (or `scripts/01-qc/`). Update HANDOFF; do not store thresholds only in chat.
