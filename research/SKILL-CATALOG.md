# Skill catalog

Prefer the matching Wisp skill. Use a Cursor built-in skill only when the row says so.

| Task | Use first | Then |
| --- | --- | --- |
| Literature, PubMed, reviews, DOI checks | `/literature-review` + `wisp-bio` (`pubmed`, `literature`) | — |
| Local PDFs | `/pdf-explore` | — |
| GEO / archives / public datasets | `/public-data-access` + `wisp-bio` (`omics-archives`) | — |
| Multi-step analysis, Methods capture | `/analysis-workflow` | Cursor file/terminal to land scripts |
| scRNA-seq QC | `/singlecell-qc` | Do not auto-filter |
| Scientific figures | `/figure-composer` | `/canvas` only for interactive demos |
| Paper narrative / Methods prose | `/paper-narrative` | — |
| Python 3.12 env, deps | `/local-env-setup` | — |
| Read/write HANDOFF | `/wisp-handoff` | Always, at start and end |
| Git, PR, refactor this adapter | Cursor `/review`, `/create-rule`, `/split-to-prs` | Not literature skills |
| Later Wisp plugins | After `python -m tools.sync_wisp_skills`, use the new `/name` | Follow that skill's description |

Explicit `/skill-name` always wins.
