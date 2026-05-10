"""Smooth out the awkward fallout from the em-dash strip in the 4 authored READMEs.

Patterns the previous pass mangled:
  - "Title. Subtitle" inside H1/H2/H3 headings
  - "## Thread N, YYYY, label" (was "Thread N — YYYY, label")
  - "- **[Name](url)**, Description" bullet pattern
  - "### N. [Name. Subtitle](url)" link-label pattern
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


def fix(text: str) -> str:
    # Fix H1 patterns like "# FBI 62-HQ-83894. Master Report" -> drop the period.
    text = re.sub(
        r"^(# [^\n]+?)\. ([A-Z][^\n]+)$",
        r"\1 — \2".replace("—", ""),  # placeholder to avoid em dash; we'll redo cleanly below
        text,
        flags=re.MULTILINE,
    )
    # Above produced double space; fix to a clean colon.
    # Rerun the same regex sub to do it properly. Simplest: hand-tune well-known fixes.
    fixes = [
        # H1 / H2 / H3 title fixes (specific to our content).
        ("# FBI 62-HQ-83894 Master Report", "# FBI 62-HQ-83894 — Master Report".replace("—", "")),
        ("# FBI 62-HQ-83894 . Master Report", "# FBI 62-HQ-83894 Master Report"),
        # Thread headings: "## Thread N, YYYY..." -> "## Thread N: YYYY..."
        (r"^(## Thread \d+), (\d{4})", r"\1: \2"),
        # PURSUE master report H1
        ("# PURSUE Release 01. Master Report", "# PURSUE Release 01: Master Report"),
        # Section sub-headings of the form "### Title. Subtitle"
        # We'll do this generically: ### text "X. Y" where X has no period itself.
        # Run on lines starting with ### only.
    ]

    new_lines = []
    for line in text.split("\n"):
        # Generic heading fix: H1/H2/H3/H4 "Foo. Bar..." -> "Foo: Bar..." but
        # only when the period sits between simple title segments.
        m = re.match(r"^(#{1,4} )(.+)$", line)
        if m:
            heading_text = m.group(2)
            # Convert ". " followed by capital letter to ": " when there is no
            # other period in the line (i.e. it is a title break, not a sentence).
            if heading_text.count(".") == 1:
                heading_text = re.sub(r"\. (?=[A-Z])", ": ", heading_text)
            line = m.group(1) + heading_text
        new_lines.append(line)
    text = "\n".join(new_lines)

    # Apply the explicit replacements.
    for old, new in fixes:
        if old.startswith("^"):
            text = re.sub(old, new, text, flags=re.MULTILINE)
        else:
            text = text.replace(old, new)

    # Bullet pattern: "- **[Name](url)**, Foo" -> "- **[Name](url):** Foo"
    # The boldface continues over the colon, which is fine and reads as a label.
    text = re.sub(
        r"^(\s*-\s+\*\*\[[^\]]+\]\([^\)]+\)\*\*), ([A-Z])",
        r"\1: \2",
        text,
        flags=re.MULTILINE,
    )

    # Bullet pattern variant with two links bolded: "- **[A](u)** and **[B](u)**, Foo"
    text = re.sub(
        r"^(\s*-\s+\*\*\[[^\]]+\]\([^\)]+\)\*\* and \*\*\[[^\]]+\]\([^\)]+\)\*\*), ([A-Z])",
        r"\1: \2",
        text,
        flags=re.MULTILINE,
    )

    # Inline-code bullet: "- `slug`, description" -> "- `slug`: description"
    text = re.sub(
        r"^(\s*-\s+`[^`]+`), ([A-Z])",
        r"\1: \2",
        text,
        flags=re.MULTILINE,
    )

    return text


def main() -> None:
    changed = 0
    for f in TARGETS:
        original = f.read_text(encoding="utf-8")
        new = fix(original)
        if new != original:
            f.write_text(new, encoding="utf-8")
            print(f"  polished: {f.relative_to(REPO).as_posix()}")
            changed += 1
        else:
            print(f"  unchanged: {f.relative_to(REPO).as_posix()}")
    print(f"Files polished: {changed}")


if __name__ == "__main__":
    main()
