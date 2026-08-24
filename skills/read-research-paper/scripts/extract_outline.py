#!/usr/bin/env python3
"""Extract title, abstract, and section headings from a readable PDF."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print(json.dumps({"error": "pypdf not installed. Run extract_outline.sh instead."}))
    sys.exit(2)


SECTION_RE = re.compile(
    r"^(\d+(?:\.\d+)*)\s+([A-Z][^\n]{2,60})$",
    re.MULTILINE,
)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60]


def extract_outline(path: Path) -> dict:
    reader = PdfReader(str(path))
    full_text = "\n".join((p.extract_text() or "") for p in reader.pages)

    # Title: first substantial line before author emails / Abstract
    title = "Unknown title"
    for line in full_text.splitlines():
        line = line.strip()
        if len(line) > 15 and "@" not in line and line.lower() != "abstract":
            title = line
            break

    abstract = ""
    abstract_match = re.search(
        r"Abstract\s*(.*?)(?=\n\s*1\s+Introduction|\n\s*Introduction|\n\s*I\.\s)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )
    if abstract_match:
        abstract = re.sub(r"\s+", " ", abstract_match.group(1)).strip()

    sections: list[dict] = []
    seen: set[str] = set()
    for match in SECTION_RE.finditer(full_text):
        number, heading = match.group(1), match.group(2).strip()
        if heading.lower() in {"abstract", "references", "acknowledgments"}:
            continue
        key = f"{number} {heading}"
        if key not in seen and float(number.split(".")[0]) <= 20:
            seen.add(key)
            sections.append({"number": number, "heading": heading})

    return {
        "path": str(path),
        "slug": slugify(title),
        "title": title,
        "abstract": abstract,
        "page_count": len(reader.pages),
        "sections": sections[:12],
    }


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: extract_outline.py <path-to.pdf>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(extract_outline(Path(sys.argv[1])), indent=2))


if __name__ == "__main__":
    main()
