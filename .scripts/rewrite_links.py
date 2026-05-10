"""
One-shot link rewriter.

After the initial Obsidian -> backtick conversion, every former [[wiki-link]]
lives in the repo as `slug`. This script walks every .md file outside raw/,
finds the slugs we know, and rewrites them as proper relative markdown links.

Run from the repo root:
    python .scripts/rewrite_links.py
"""

from __future__ import annotations

import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# slug (Obsidian filename without .md) -> path relative to repo root
SLUG_TO_PATH: dict[str, str] = {
    # PURSUE cases (renamed)
    "2026-05-08-apollo-17-vm6-triangular-formation":   "pursue-release-01/cases/apollo-17-vm6.md",
    "2026-05-08-bronze-ellipsoid-september-2023":      "pursue-release-01/cases/bronze-ellipsoid.md",
    "2026-05-08-usper-statement-orb-helicopter-chase": "pursue-release-01/cases/usper-statement.md",
    "2026-05-08-orbs-launching-orbs-western-us":       "pursue-release-01/cases/orbs-launching-orbs.md",
    "2026-05-08-mexico-congress-alien-corpses-cable":  "pursue-release-01/cases/mexico-2003-alien-corpses.md",
    "2026-05-08-kazakhstan-1994-747-cable":            "pursue-release-01/cases/kazakhstan-1994-747.md",

    # PURSUE coverage (renamed)
    "2026-05-08-tyson-anticlimactic-prediction": "pursue-release-01/coverage/tyson-anticlimactic-prediction.md",
    "2026-05-08-newspaceeconomy-pursue-analysis": "pursue-release-01/coverage/newspaceeconomy-analysis.md",
    "2026-05-08-washtimes-trump-ufo-files":      "pursue-release-01/coverage/washtimes-trump-ufo-files.md",
    "2026-05-08-mirror-football-uap":            "pursue-release-01/coverage/mirror-football-uap.md",
    "2026-05-08-pentagon-ufo-files-stripes":     "pursue-release-01/coverage/stars-and-stripes.md",
    "2026-05-08-pentagon-ufo-files-fox":         "pursue-release-01/coverage/fox-news.md",
    "2026-05-08-pentagon-ufo-files-cbs":         "pursue-release-01/coverage/cbs-news.md",

    # PURSUE master report + inventory
    "2026-05-08-pentagon-ufo-files-drop":           "pursue-release-01/README.md",
    "2026-05-08-pursue-release-01-full-inventory":  "pursue-release-01/full-inventory.md",
    "2026-05-08-pursue-release-01-log":             "pursue-release-01/full-inventory.md",  # log was rolled into inventory

    # FBI inventory
    "2026-05-09-fbi-62hq83894-full-inventory":      "fbi-62hq83894/full-inventory.md",

    # Context (entities)
    "aaro":                  "context/aaro.md",
    "pursue-program":        "context/pursue-program.md",
    "department-of-war":     "context/department-of-war.md",
    "pete-hegseth":          "context/pete-hegseth.md",
    "neil-degrasse-tyson":   "context/neil-degrasse-tyson.md",

    # Concepts
    "uap-disclosure":        "context/uap-disclosure.md",
}

# Auto-populate FBI cases by walking fbi-62hq83894/cases/
fbi_cases_dir = REPO / "fbi-62hq83894" / "cases"
for case_file in fbi_cases_dir.glob("*.md"):
    case_slug = case_file.stem
    for prefix in ("2026-05-08-fbi-62hq83894-", "2026-05-09-fbi-62hq83894-", "2026-05-10-fbi-62hq83894-"):
        SLUG_TO_PATH[f"{prefix}{case_slug}"] = f"fbi-62hq83894/cases/{case_slug}.md"


# Hand-tuned display labels for slugs whose stripped form is unhelpful.
DISPLAY_OVERRIDES: dict[str, str] = {
    "2026-05-08-pentagon-ufo-files-drop":          "PURSUE master report",
    "2026-05-08-pursue-release-01-full-inventory": "PURSUE full inventory",
    "2026-05-08-pursue-release-01-log":            "PURSUE full inventory",
    "2026-05-09-fbi-62hq83894-full-inventory":    "FBI 62-HQ-83894 case index",
    "2026-05-08-pentagon-ufo-files-cbs":          "CBS News coverage",
    "2026-05-08-pentagon-ufo-files-fox":          "Fox News coverage",
    "2026-05-08-pentagon-ufo-files-stripes":      "Stars and Stripes coverage",
    "2026-05-08-mirror-football-uap":             "Mirror, football-UAP framing",
    "2026-05-08-washtimes-trump-ufo-files":       "Washington Times coverage",
    "2026-05-08-tyson-anticlimactic-prediction":  "Tyson — anticlimactic prediction",
    "2026-05-08-newspaceeconomy-pursue-analysis": "New Space Economy — what 'unresolved' means",
    "2026-05-08-apollo-17-vm6-triangular-formation":   "Apollo 17 VM6",
    "2026-05-08-bronze-ellipsoid-september-2023":      "Bronze Ellipsoid (Sept 2023)",
    "2026-05-08-usper-statement-orb-helicopter-chase": "USPER Statement",
    "2026-05-08-orbs-launching-orbs-western-us":       "Western US orbs launching orbs",
    "2026-05-08-mexico-congress-alien-corpses-cable":  "Mexico 2003 alien corpses cable",
    "2026-05-08-kazakhstan-1994-747-cable":            "Kazakhstan 1994 747 encounter",
    "uap-disclosure":      "UAP disclosure (concept)",
    "aaro":                "AARO",
    "pursue-program":      "PURSUE program",
    "department-of-war":   "Department of War",
    "pete-hegseth":        "Pete Hegseth",
    "neil-degrasse-tyson": "Neil deGrasse Tyson",
}


def display_name(slug: str) -> str:
    """Convert a slug into a readable label."""
    if slug in DISPLAY_OVERRIDES:
        return DISPLAY_OVERRIDES[slug]
    # Strip 2026-MM-DD-
    s = re.sub(r"^2026-\d{2}-\d{2}-", "", slug)
    # Strip fbi-62hq83894- archive prefix (keeps the case name)
    s = re.sub(r"^fbi-62hq83894-", "", s)
    # Strip pursue-release-01- and pentagon-ufo-files-
    s = re.sub(r"^(pursue-release-01-|pentagon-ufo-files-)", "", s)
    return s


def relpath(from_file: Path, to_path_rel_root: str) -> str:
    """Compute a forward-slash relative path from from_file to a repo-root-relative target."""
    target = (REPO / to_path_rel_root).resolve()
    src_dir = from_file.parent.resolve()
    rel = os.path.relpath(target, src_dir)
    return rel.replace(os.sep, "/")


# Patterns we want to rewrite. Two forms:
# 1. `slug`            (inline-code form left over from the [[slug]] -> `slug` pass)
# 2. - `slug` -- desc  (Connections list items)
# We match the simpler universal pattern: `slug` where slug is a key in SLUG_TO_PATH.
BACKTICK_SLUG_RE = re.compile(r"`([^`\n]+?)`")


def rewrite_file(md_path: Path) -> tuple[int, int]:
    """Rewrite all known backticked slugs in md_path. Returns (matched, rewritten)."""
    text = md_path.read_text(encoding="utf-8")
    matched = 0
    rewritten = 0

    def sub(m: re.Match) -> str:
        nonlocal matched, rewritten
        slug = m.group(1)
        matched += 1
        if slug in SLUG_TO_PATH:
            target = SLUG_TO_PATH[slug]
            rel = relpath(md_path, target)
            label = display_name(slug)
            rewritten += 1
            return f"[{label}]({rel})"
        return m.group(0)  # leave unknown backticked content alone

    new_text = BACKTICK_SLUG_RE.sub(sub, text)
    if new_text != text:
        md_path.write_text(new_text, encoding="utf-8")
    return matched, rewritten


# Second pass: update display labels on already-rewritten links.
# Matches [old-label](path-suffix) where path-suffix is one of our targets.
LABEL_FIX_RE = re.compile(r"\[([^\]\n]+?)\]\(([^)\n]+?)\)")

# Map a repo-root-relative target path -> preferred display label.
# Keyed on full repo-relative path so we can disambiguate identically-named
# files (e.g. pursue-release-01/full-inventory.md vs fbi-62hq83894/full-inventory.md).
PATH_TO_LABEL: dict[str, str] = {}
for slug, target in SLUG_TO_PATH.items():
    label = DISPLAY_OVERRIDES.get(slug)
    if label:
        PATH_TO_LABEL[target] = label


def fix_labels(md_path: Path) -> int:
    text = md_path.read_text(encoding="utf-8")
    fixed = 0

    def sub(m: re.Match) -> str:
        nonlocal fixed
        old_label, path = m.group(1), m.group(2)
        # External link, leave alone
        if path.startswith("http://") or path.startswith("https://"):
            return m.group(0)
        # Anchors-only or non-md, leave alone
        if not path.endswith(".md") and ".md#" not in path:
            return m.group(0)
        # Resolve the link target back to a repo-relative posix path.
        link_target = path.split("#", 1)[0]
        try:
            abs_target = (md_path.parent / link_target).resolve()
            rel_target = abs_target.relative_to(REPO).as_posix()
        except (ValueError, OSError):
            return m.group(0)
        better = PATH_TO_LABEL.get(rel_target)
        if not better or old_label == better:
            return m.group(0)
        # Touch when:
        # - Old label is slug-form (no spaces), OR
        # - Old label is a previously-applied auto label that's now wrong
        #   for this path (basename collision case). Detect this by checking
        #   if old_label appears in DISPLAY_OVERRIDES.values() — i.e. it's
        #   one of OUR labels, just on the wrong link.
        if " " in old_label and old_label not in DISPLAY_OVERRIDES.values():
            return m.group(0)
        fixed += 1
        return f"[{better}]({path})"

    new_text = LABEL_FIX_RE.sub(sub, text)
    if new_text != text:
        md_path.write_text(new_text, encoding="utf-8")
    return fixed


def main() -> None:
    targets: list[Path] = []
    for md_path in REPO.rglob("*.md"):
        rel = md_path.relative_to(REPO).as_posix()
        if rel.startswith("raw/"):
            continue
        if rel.startswith(".scripts/"):
            continue
        targets.append(md_path)

    total_matched = 0
    total_rewritten = 0
    total_relabeled = 0
    files_changed = 0
    files_relabeled = 0

    for md_path in targets:
        matched, rewritten = rewrite_file(md_path)
        total_matched += matched
        total_rewritten += rewritten
        if rewritten:
            files_changed += 1
        relabeled = fix_labels(md_path)
        total_relabeled += relabeled
        if relabeled:
            files_relabeled += 1

    print(f"Files scanned: {len(targets)}")
    print(f"Pass 1 — backtick slug -> link conversion:")
    print(f"  Files changed: {files_changed}")
    print(f"  Backtick-code spans inspected: {total_matched}")
    print(f"  Rewritten to relative links: {total_rewritten}")
    print(f"Pass 2 — display label cleanup:")
    print(f"  Files changed: {files_relabeled}")
    print(f"  Labels improved: {total_relabeled}")


if __name__ == "__main__":
    main()
