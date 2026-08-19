# Skill catalog

Prefer the matching Wisp skill. Use a Cursor built-in skill only when the row says so.

| Task | Use first | Then |
| --- | --- | --- |
| Literature, PubMed, reviews, DOI checks, HTML/PDF report | `/literature-review` + `wisp-bio` (`pubmed`) | Write `results/reports/*.html` |
| Local PDFs | `/pdf-explore` | — |
| GEO / archives / public datasets | `/public-data-access` + `wisp-bio` (`omics-archives`) | — |
| Multi-step analysis, Methods capture | `/analysis-workflow` | Cursor file/terminal to land scripts |
| scRNA-seq QC | `/singlecell-qc` | Do not auto-filter |
| Scientific figures (compose) | `/figure-composer` | `/canvas` only for interactive demos |
| Figure gallery search (if the plugin is installed) | `/figure-library` + `figure-library` MCP | Visual review before materialize |
| Paper narrative / Methods prose | `/paper-narrative` | — |
| Journal club slides | `/journal-club-ppt` | — |
| Python 3.12 env, deps | `/local-env-setup` | — |
| Remote SSH compute | `/remote-compute-ssh` | `/probe-compute-environment` |
| Read/write `research/HANDOFF.md` | `/wisp-handoff` | Always, at start and end |
| Continue a WS task in a bare topic folder (wire overlay + HANDOFF) | `/ws-continue` | New chat in the topic folder; path under the Wisp topics root auto-fires, or say a passphrase (见 [docs/bridge-usage.html](../docs/bridge-usage.html)) |
| Git, PR, refactor this adapter | Cursor `/review`, `/create-rule`, `/split-to-prs` | Not literature skills |
| Later Wisp plugins | After `python -m tools.sync_wisp_skills`, use the new `/name` | Follow that skill’s description |

Explicit `/skill-name` always wins.
