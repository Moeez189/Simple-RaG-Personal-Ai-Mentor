"""One-time helper: promote ### to ## and strip numbered ## prefixes in markdown KB files."""

from __future__ import annotations

import re
from pathlib import Path

DATA_FILES = [
    Path("data/React Native Notes/React_Native_Interview_Knowledge_Base.md"),
]


def restructure(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("### "):
            lines.append("## " + line[4:])
        elif re.match(r"^## \d+\.\s+", line):
            lines.append(re.sub(r"^## \d+\.\s+", "## ", line))
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def main() -> None:
    for path in DATA_FILES:
        path.write_text(restructure(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"Restructured {path}")


if __name__ == "__main__":
    main()
