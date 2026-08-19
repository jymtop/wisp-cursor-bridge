---
name: local-env-setup
description: Set up a local Python 3.12 environment with uv for this project. Use when deps, kernels, or Windows path issues block analysis.
---
<!-- wisp-cursor-adapter: true -->

# Local env setup (Cursor adapter)

```powershell
uv sync --python 3.12
uv run --python 3.12 python -c "import sys; print(sys.version)"
```

- Require Python 3.12. Do not silently use 3.11 or 3.13.
- Prefer `uv add` for new analysis libraries; record them in `pyproject.toml`.
- Do not install KEGG commercial clients or undeclared binaries.
- After the env works, update HANDOFF `next` to the scientific step, not more setup.
