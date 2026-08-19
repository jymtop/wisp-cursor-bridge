"""Parse and update research/HANDOFF.md (wisp.handoff.v1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

SCALAR_KEYS = (
    "last_app",
    "last_at",
    "status",
    "question",
    "next",
)
LIST_KEYS = ("key_files", "open_questions", "do_not")


@dataclass
class Handoff:
    last_app: str = ""
    last_at: str = ""
    status: str = "in_progress"
    question: str = ""
    next: str = ""
    key_files: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    do_not: list[str] = field(default_factory=list)
    extra: str = ""

    def render(self) -> str:
        lines = [
            "# HANDOFF",
            "",
            f"- last_app: {self.last_app}",
            f"- last_at: {self.last_at}",
            f"- status: {self.status}",
            f"- question: {self.question}",
            f"- next: {self.next}",
            "- key_files:",
        ]
        lines.extend(f"  - {item}" for item in self.key_files)
        if not self.key_files:
            lines.append("  -")
        lines.append("- open_questions:")
        lines.extend(f"  - {item}" for item in self.open_questions)
        if not self.open_questions:
            lines.append("  -")
        lines.append("- do_not:")
        lines.extend(f"  - {item}" for item in self.do_not)
        if not self.do_not:
            lines.append("  -")
        if self.extra.strip():
            lines.extend(["", self.extra.strip(), ""])
        else:
            lines.append("")
        return "\n".join(lines)


def parse_handoff(text: str) -> Handoff:
    data = Handoff()
    current_list: str | None = None
    extra_lines: list[str] = []
    in_header = True
    for raw in text.splitlines():
        line = raw.rstrip()
        if in_header and line.startswith("# "):
            continue
        if in_header and not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and not line.startswith("  -"):
            body = stripped[2:]
            if ":" in body:
                key, _, value = body.partition(":")
                key = key.strip()
                value = value.strip()
                if key in SCALAR_KEYS:
                    setattr(data, key, value)
                    current_list = None
                    continue
                if key in LIST_KEYS:
                    current_list = key
                    if value and value != "-":
                        getattr(data, key).append(value)
                    continue
            extra_lines.append(line)
            in_header = False
            current_list = None
            continue
        if current_list and line.startswith("  -"):
            item = line[3:].strip()
            if item and item != "-":
                getattr(data, current_list).append(item)
            continue
        if stripped:
            in_header = False
            extra_lines.append(line)
            current_list = None
    data.extra = "\n".join(extra_lines).strip()
    return data


def load_handoff(path: Path) -> Handoff:
    return parse_handoff(path.read_text(encoding="utf-8"))


def write_handoff(path: Path, handoff: Handoff) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(handoff.render(), encoding="utf-8")


def continue_from_wisp(
    path: Path,
    *,
    next_step: str,
    key_files: list[str] | None = None,
    last_app: str = "cursor",
) -> Handoff:
    handoff = load_handoff(path) if path.is_file() else Handoff()
    handoff.last_app = last_app
    handoff.last_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    handoff.next = next_step
    if key_files:
        for item in key_files:
            if item not in handoff.key_files:
                handoff.key_files.append(item)
    write_handoff(path, handoff)
    return handoff
