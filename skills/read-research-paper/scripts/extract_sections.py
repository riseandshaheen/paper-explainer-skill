#!/usr/bin/env python3
"""Extract per-section body text with page numbers from a readable PDF.

Unlike extract_outline.py (headings only), this returns the actual prose of each
section so explanations can be grounded in the paper rather than recalled.
"""

from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print(json.dumps({"error": "pypdf not installed. Run extract_sections.sh instead."}))
    sys.exit(2)


PAGE_SEP = "\n\x0c\n"

NUMBERED_HEADING_RE = re.compile(
    r"^[ \t]*(\d{1,2}(?:\.\d{1,2})*)\.?[ \t]+([A-Z][^\n]{2,70}?)[ \t]*$",
    re.MULTILINE,
)

# IEEE style: "I. Introduction" with "A. Subsection" beneath it.
ROMAN_HEADING_RE = re.compile(
    r"^[ \t]*((?:[IVXL]{1,6}|[A-Z]))\.[ \t]+([A-Z][^\n]{2,70}?)[ \t]*$",
    re.MULTILINE,
)

ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

# Papers that don't number their sections still use a predictable vocabulary.
UNNUMBERED_HEADINGS = (
    "Introduction",
    "Background",
    "Related Work",
    "Previous Work",
    "Motivation",
    "Preliminaries",
    "Method",
    "Methods",
    "Methodology",
    "Approach",
    "Model",
    "Architecture",
    "Experiments",
    "Experimental Setup",
    "Evaluation",
    "Results",
    "Discussion",
    "Limitations",
    "Future Work",
    "Conclusion",
    "Conclusions",
)

UNNUMBERED_HEADING_RE = re.compile(
    r"^[ \t]*(" + "|".join(UNNUMBERED_HEADINGS) + r")[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)

SKIP_HEADINGS = {"abstract", "references", "acknowledgments", "acknowledgements"}

# Author initials in a bibliography ("A. Rowstron, Eds.") look exactly like
# lettered subsections, so body text stops here.
REFERENCES_RE = re.compile(r"\b(?:R\s?EFERENCES|References|BIBLIOGRAPHY|Bibliography)\b")

SKIP_TITLE_LINE_RE = re.compile(r"^(?:arxiv:|doi:|https?://|\d+$)", re.IGNORECASE)


def roman_to_int(token: str) -> int:
    total = 0
    highest = 0
    for char in reversed(token):
        value = ROMAN_VALUES.get(char, 0)
        if value == 0:
            return 0
        total += -value if value < highest else value
        highest = max(highest, value)
    return total


def normalize_heading(text: str) -> str:
    """Undo small-caps artifacts ("I NTRODUCTION") and shout-case headings."""
    text = re.sub(r"\b([A-Z]) ([A-Z]+)\b", r"\1\2", text).strip()
    words = text.split()
    if words and all(w.isupper() or not w.isalpha() for w in words):
        text = " ".join(w.capitalize() if w.isalpha() else w for w in words)
    return text


def slugify(text: str, limit: int = 40) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return text.strip("-")[:limit] or "section"


def load_pages(reader: PdfReader) -> list[str]:
    pages: list[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001 - a single bad page shouldn't sink the run
            pages.append("")
    return pages


def build_offset_index(pages: list[str]) -> tuple[str, list[int]]:
    """Join pages into one string, tracking where each page starts."""
    starts: list[int] = []
    offset = 0
    for text in pages:
        starts.append(offset)
        offset += len(text) + len(PAGE_SEP)
    return PAGE_SEP.join(pages), starts


def page_for_offset(starts: list[int], offset: int) -> int:
    return bisect.bisect_right(starts, offset)


def clean(text: str) -> str:
    text = re.sub(r"-\n(?=[a-z])", "", text)  # rejoin hyphen-split words
    text = text.replace("\x0c", " ")
    return re.sub(r"\s+", " ", text).strip()


def _candidate(number: str, heading: str, match: re.Match) -> dict | None:
    heading = normalize_heading(heading)
    if heading.lower() in SKIP_HEADINGS or len(heading) < 3:
        return None
    return {"number": number, "heading": heading, "start": match.start(), "end": match.end()}


def _numbered_candidates(full_text: str) -> list[dict]:
    found: list[dict] = []
    for match in NUMBERED_HEADING_RE.finditer(full_text):
        number = match.group(1)
        if int(number.split(".")[0]) > 20:
            continue
        cand = _candidate(number, match.group(2), match)
        if cand:
            found.append(cand)
    return found


def _roman_candidates(full_text: str) -> list[dict]:
    """Roman sections with lettered subsections, disambiguated by expected order."""
    found: list[dict] = []
    expected = 1
    current = ""
    for match in ROMAN_HEADING_RE.finditer(full_text):
        token = match.group(1)
        if roman_to_int(token) == expected:
            number = token
            expected += 1
            current = token
        elif len(token) == 1 and current:
            number = f"{current}.{token}"
        else:
            continue
        cand = _candidate(number, match.group(2), match)
        if cand:
            found.append(cand)
    return found


def _unnumbered_candidates(full_text: str) -> list[dict]:
    found: list[dict] = []
    for match in UNNUMBERED_HEADING_RE.finditer(full_text):
        cand = _candidate("", match.group(1), match)
        if cand:
            found.append(cand)
    return found


def find_headings(full_text: str) -> list[dict]:
    """Locate candidate headings, keeping the occurrence with the most body text."""
    candidates: list[dict] = []
    for builder in (_numbered_candidates, _roman_candidates, _unnumbered_candidates):
        candidates = builder(full_text)
        if len(candidates) >= 3:
            break

    if not candidates:
        return []

    # A heading listed in a table of contents repeats later with the real body.
    # Keep whichever occurrence is followed by the most text before the next heading.
    boundaries = sorted(c["start"] for c in candidates)
    best: dict[str, dict] = {}
    for cand in candidates:
        following = bisect.bisect_right(boundaries, cand["start"])
        next_start = boundaries[following] if following < len(boundaries) else len(full_text)
        cand["body_len"] = next_start - cand["end"]
        key = f"{cand['number']} {cand['heading']}".strip().lower()
        if key not in best or cand["body_len"] > best[key]["body_len"]:
            best[key] = cand

    return sorted(best.values(), key=lambda c: c["start"])


def extract_abstract(full_text: str, starts: list[int]) -> dict:
    match = re.search(
        r"\bAbstract\b\s*[:.\-]?\s*(.*?)(?=\n\s*1[\s.]+Introduction|\n\s*Introduction\b|\n\s*I\.\s)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return {"text": "", "page": None}
    return {
        "text": clean(match.group(1)),
        "page": page_for_offset(starts, match.start(1)),
    }


def references_offset(full_text: str) -> int:
    """Offset where the bibliography starts, or end of text if not found."""
    cutoff = int(len(full_text) * 0.45)
    matches = [m.start() for m in REFERENCES_RE.finditer(full_text) if m.start() >= cutoff]
    return matches[-1] if matches else len(full_text)


def title_candidates(full_text: str) -> list[str]:
    """Front-matter lines that could be the title; PDFs often split it across lines."""
    found: list[str] = []
    for line in full_text.splitlines()[:40]:
        line = line.strip()
        if len(line) < 12 or "@" in line or line.lower() == "abstract":
            continue
        if SKIP_TITLE_LINE_RE.match(line):
            continue
        found.append(line)
        if len(found) == 3:
            break
    return found


def extract_sections(path: Path, max_chars: int, only: str | None) -> dict:
    reader = PdfReader(str(path))
    pages = load_pages(reader)
    full_text, starts = build_offset_index(pages)

    body_limit = references_offset(full_text)
    headings = [h for h in find_headings(full_text) if h["start"] < body_limit]
    sections: list[dict] = []

    for i, head in enumerate(headings):
        body_end = headings[i + 1]["start"] if i + 1 < len(headings) else body_limit
        body = full_text[head["end"] : body_end]
        cleaned = clean(body)
        if len(cleaned) < 40:  # running headers and figure captions, not real sections
            continue

        label = f"{head['number']} {head['heading']}".strip()
        sections.append(
            {
                "number": head["number"],
                "heading": head["heading"],
                "label": label,
                "id": slugify(head["heading"]),
                "page_start": page_for_offset(starts, head["start"]),
                "page_end": page_for_offset(starts, max(head["end"], body_end - 1)),
                "char_count": len(cleaned),
                "truncated": len(cleaned) > max_chars,
                "text": cleaned[:max_chars],
            }
        )

    if only:
        needle = only.lower()
        sections = [
            s
            for s in sections
            if s["number"] == only or needle in s["heading"].lower() or s["id"] == needle
        ]

    titles = title_candidates(full_text)
    return {
        "path": str(path),
        "title": titles[0] if titles else "Unknown title",
        "title_candidates": titles,
        "page_count": len(pages),
        "abstract": extract_abstract(full_text, starts),
        "section_count": len(sections),
        "sections": sections,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument(
        "--max-chars",
        type=int,
        default=6000,
        help="Cap per-section text (default 6000)",
    )
    parser.add_argument(
        "--section",
        help="Only this section, matched by number, id, or heading substring",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Print readable text instead of JSON",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        print(json.dumps({"error": f"File not found: {args.pdf}"}), file=sys.stderr)
        sys.exit(1)

    result = extract_sections(args.pdf, args.max_chars, args.section)

    if args.text:
        print(f"# {result['title']}  ({result['page_count']} pages)\n")
        if result["abstract"]["text"]:
            print(f"## Abstract  [p.{result['abstract']['page']}]\n")
            print(result["abstract"]["text"] + "\n")
        for section in result["sections"]:
            pages = (
                f"p.{section['page_start']}"
                if section["page_start"] == section["page_end"]
                else f"p.{section['page_start']}-{section['page_end']}"
            )
            print(f"## {section['label']}  [{pages}]\n")
            print(section["text"] + "\n")
    else:
        print(json.dumps(result, indent=2))

    if result["section_count"] == 0:
        print(
            "WARNING: no sections detected. Layout may be unusual; fall back to --text on the whole PDF.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
