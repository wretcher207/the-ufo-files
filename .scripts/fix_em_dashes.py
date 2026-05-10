"""Replace em dashes in the 4 authored README files only.

Em dashes are not allowed in delivered prose per CLAUDE.md. The case files
(under */cases/, /coverage/, /context/) are content copied from David's
Obsidian wiki, so we leave those alone. This script only touches the
top-level README and the 3 section READMEs.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

TARGETS = [
    REPO / "README.md",
    REPO / "pursue-release-01" / "README.md",
    REPO / "fbi-62hq83894" / "README.md",
    REPO / "raw" / "README.md",
]


def fix(text: str) -> tuple[str, int]:
    count = text.count("—")
    # Substitution rules, applied in order.
    rules = [
        # " — " between lowercase / digits  -> ", "
        (re.compile(r"(?<=[a-z0-9])\s—\s(?=[a-z0-9])"), ", "),
        # " — " starting a list-item-like clarification (after letter, before
        # capital) -> ". " creates a sentence break, more natural.
        (re.compile(r"(?<=[a-z0-9.,?!\)])\s—\s(?=[A-Z])"), ". "),
        # Em dash between digits (date ranges or numbers) -> en dash.
        (re.compile(r"(?<=\d)—(?=\d)"), "–"),
        # Catch-all fallback: replace any remaining " — " with ", ".
        (re.compile(r"\s—\s"), ", "),
        # Lone em dash at end of line -> comma.
        (re.compile(r"\s—$"), ","),
        # Any stragglers.
        (re.compile(r"—"), ","),
    ]
    for pat, repl in rules:
        text = pat.sub(repl, text)
    # Clean up artifacts.
    text = re.sub(r",\s+,", ",", text)
    text = re.sub(r"\.\s+\.\s", ". ", text)
    return text, count


def main() -> None:
    total_replaced = 0
    for f in TARGETS:
        original = f.read_text(encoding="utf-8")
        new, n = fix(original)
        if new != original:
            f.write_text(new, encoding="utf-8")
            print(f"  {f.relative_to(REPO).as_posix()}: {n} em dashes replaced")
            total_replaced += n
        else:
            print(f"  {f.relative_to(REPO).as_posix()}: no changes")
    print(f"Total em dashes replaced: {total_replaced}")


if __name__ == "__main__":
    main()
