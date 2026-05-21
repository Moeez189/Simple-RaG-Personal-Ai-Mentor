"""Validate markdown knowledge-base files under data/ for RAG-friendly structure."""

from __future__ import annotations

import re
import sys
from pathlib import Path

DATA_DIR = Path("data")
MARKDOWN_GLOB = "**/*.md"
MAX_SECTION_CHARS = 1200
MAX_PARAGRAPH_LINES = 8
NUMBERED_HEADING = re.compile(r"^##\s+\d+\.\s+")


def _iter_markdown_files():
    for path in sorted(DATA_DIR.glob(MARKDOWN_GLOB)):
        if path.name == "README.md":
            continue
        yield path


def _strip_fenced_code(text: str) -> str:
    lines = []
    in_code = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            lines.append(line)
    return "\n".join(lines)


def _parse_sections(text: str) -> list[dict]:
    sections = []
    current = None

    for line in text.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections.append(current)
            current = {
                "heading": line[3:].strip(),
                "lines": [],
                "subsections": 0,
            }
            continue

        if line.startswith("### ") and current is not None:
            current["subsections"] += 1

        if current is not None:
            current["lines"].append(line)

    if current is not None:
        sections.append(current)

    return sections


def _check_file(path: Path) -> list[str]:
    issues = []
    text = path.read_text(encoding="utf-8")
    rel = path.as_posix()

    if not text.lstrip().startswith("# "):
        issues.append(f"{rel}: missing top-level '# Document title' heading")

    sections = _parse_sections(text)

    for section in sections:
        heading = section["heading"]
        body = "\n".join(section["lines"]).strip()
        prose_body = _strip_fenced_code(body).strip()
        body_len = len(prose_body)

        if NUMBERED_HEADING.match(f"## {heading}"):
            issues.append(
                f"{rel}: numbered ## heading '{heading}' — use a concept name "
                "(e.g. '## Debouncing' not '## 24. Advanced...')"
            )

        if section["subsections"] > 0:
            issues.append(
                f"{rel}: ## '{heading}' contains {section['subsections']} ### subsection(s). "
                "Promote each ### to its own ## (one concept per ##)."
            )

        if body_len > MAX_SECTION_CHARS:
            issues.append(
                f"{rel}: ## '{heading}' body is {body_len} chars "
                f"(>{MAX_SECTION_CHARS}). Split into smaller ## sections."
            )

        paragraph_lengths = [
            len(paragraph.splitlines())
            for paragraph in prose_body.split("\n\n")
            if paragraph.strip()
        ]
        if any(lines > MAX_PARAGRAPH_LINES for lines in paragraph_lengths):
            issues.append(
                f"{rel}: ## '{heading}' has a long paragraph block "
                f"(>{MAX_PARAGRAPH_LINES} lines). Shorten paragraphs for 300-char chunks."
            )

    return issues


def main() -> int:
    if not DATA_DIR.exists():
        print("No data/ directory found.", file=sys.stderr)
        return 1

    all_issues: list[str] = []
    files_checked = 0

    for path in _iter_markdown_files():
        files_checked += 1
        all_issues.extend(_check_file(path))

    if files_checked == 0:
        print("No markdown knowledge files found under data/.")
        return 0

    if all_issues:
        print(f"Found {len(all_issues)} issue(s) in {files_checked} file(s):\n")
        for issue in all_issues:
            print(f"  - {issue}")
        print("\nSee data/README.md for formatting rules.")
        return 1

    print(f"All {files_checked} markdown file(s) pass RAG structure checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
