"""Stub QC entrypoint. Extend after HANDOFF; keep rerunnable on Python 3.12."""

from __future__ import annotations


def summarize(n_cells: int, n_genes: int) -> str:
    return f"matrix {n_cells} x {n_genes} (no filter applied)"


def main() -> None:
    print(summarize(0, 0))
    print("next: load a real h5ad and compute mito_frac; do not filter yet")


if __name__ == "__main__":
    main()
