"""Index Wisp bio-tools without loading all 247 schemas into the model."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from gateway.paths import DEFERRED_JSON, DOMAINS_JSON


@dataclass(frozen=True)
class BioCatalog:
    domains: dict[str, list[str]]
    deferred_tools: frozenset[str]

    def domain_names(self) -> list[str]:
        return sorted(self.domains)

    def all_tools(self) -> list[tuple[str, str]]:
        rows: list[tuple[str, str]] = []
        for domain, tools in sorted(self.domains.items()):
            for name in tools:
                if name not in self.deferred_tools:
                    rows.append((domain, name))
        return rows

    def search(self, query: str, *, domain: str | None = None, limit: int = 20) -> list[tuple[str, str]]:
        needles = [part.lower() for part in query.split() if part]
        hits: list[tuple[str, str]] = []
        for dname, tool in self.all_tools():
            if domain and dname != domain:
                continue
            hay = f"{dname} {tool}".lower()
            if not needles or all(n in hay for n in needles):
                hits.append((dname, tool))
            if len(hits) >= limit:
                break
        return hits

    def resolve(self, tool: str) -> str | None:
        for dname, name in self.all_tools():
            if name == tool:
                return dname
        return None


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_catalog(domains_path: Path | None = None, deferred_path: Path | None = None) -> BioCatalog:
    domains_file = domains_path or DOMAINS_JSON
    deferred_file = deferred_path or DEFERRED_JSON
    domains = _load_json(domains_file)
    deferred_tools: set[str] = set()
    if deferred_file.is_file():
        deferred = _load_json(deferred_file)
        deferred_tools.update(deferred.get("license_tools") or [])
        deferred_tools.update(deferred.get("tools") or [])
        for blocked in deferred.get("domains") or []:
            deferred_tools.update(domains.get(blocked) or [])
    return BioCatalog(domains=domains, deferred_tools=frozenset(deferred_tools))
