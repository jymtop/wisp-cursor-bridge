# Vendored Wisp Science assets

Sparse snapshot of https://github.com/xuzhougeng/wisp-science

- Commit: see `wisp-science/WISP_PIN.txt`
- Included: `mcp-servers/bio-tools/`, `skills/`, `LICENSE`

Refresh:

```powershell
git clone --filter=blob:none --sparse --depth 1 https://github.com/xuzhougeng/wisp-science.git wisp-science-new
Set-Location wisp-science-new
git sparse-checkout set --no-cone mcp-servers/bio-tools skills /LICENSE
# then replace ../wisp-science file tree and write the new SHA to WISP_PIN.txt
```

Do not vendor `src-tauri/`, `crates/`, or other AGPL desktop sources.
