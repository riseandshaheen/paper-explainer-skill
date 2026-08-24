#!/usr/bin/env python3
"""Validate a generated paper pack.

Structural checks always run. Passing --pdf additionally verifies that every
"From the paper" claim is grounded on the page it cites, which is the check that
catches an agent narrating from memory instead of from the paper.
"""

from __future__ import annotations

import argparse
import re
import sys
from html import unescape
from pathlib import Path

REQUIRED_FILES = ("slides.html", "deep.html", "worked.html", "glossary.html")

PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_]+\}\}")
FROM_PAPER_RE = re.compile(r'<p[^>]*class="from-paper"[^>]*>(.*?)</p>', re.S | re.I)
PAGE_ANCHOR_RE = re.compile(r"p\.\s?(\d+)(?:\s?[-\u2013]\s?(\d+))?")
# "§4.4" points at the paper, it isn't a factual claim to verify.
SECTION_ANCHOR_RE = re.compile(r"\u00a7\s?[\w.]+")
ANCHOR_HREF_RE = re.compile(r'href="#([^"]+)"')
FILE_HREF_RE = re.compile(r'href="([^"#][^"]*\.html)"')
ID_RE = re.compile(r'id="([^"]+)"')
SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.I)
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,5}\b")
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")

ACRONYM_STOPLIST = {
    "AND", "THE", "FOR", "NOT", "BUT", "YOU", "ALL", "NEW", "ONE", "TWO", "VS",
    "OK", "NO", "IF", "IS", "IT", "IN", "ON", "OF", "TO", "AS", "AT", "BY", "OR",
    "AN", "BE", "SO", "UP", "WE", "US", "HTML", "CSS", "SVG", "PDF", "III", "II",
    "IV", "VI", "VII", "IX", "XI", "A", "I", "V", "X",
}

WORD_STOPLIST = {
    "this", "that", "with", "from", "they", "them", "than", "then", "were", "have",
    "been", "which", "their", "would", "could", "about", "into", "more", "most",
    "such", "when", "what", "each", "also", "only", "over", "very", "much", "here",
    "paper", "using", "used", "these", "those", "while", "where", "both", "same",
    "other", "does", "make", "made", "will", "shows", "show", "even", "like",
}


def visible_text(html: str) -> str:
    html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return unescape(re.sub(r"\s+", " ", html))


def content_words(text: str) -> set[str]:
    return {
        w
        for w in re.findall(r"[a-z]{4,}", text.lower())
        if w not in WORD_STOPLIST
    }


def normalize_for_search(text: str) -> str:
    """Collapse whitespace so PDF-split numbers like '53. 3' still match."""
    return re.sub(r"\s+", "", text.lower())


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"{where}: {message}")


def check_structure(pack: Path, files: dict[str, str], report: Report) -> None:
    for name, html in files.items():
        for placeholder in set(PLACEHOLDER_RE.findall(html)):
            report.error(name, f"unfilled placeholder {placeholder}")

        ids = set(ID_RE.findall(html))
        for anchor in set(ANCHOR_HREF_RE.findall(html)):
            if anchor not in ids:
                report.error(name, f'anchor "#{anchor}" has no matching id')

        for target in set(FILE_HREF_RE.findall(html)):
            if not (pack / target).exists():
                report.error(name, f'link "{target}" does not exist in the pack')

        for tag in SVG_OPEN_RE.findall(html):
            if "viewBox" not in tag:
                report.warn(name, "an <svg> has no viewBox and will not scale")

        missing_nav = [f for f in REQUIRED_FILES if f'href="{f}"' not in html]
        if missing_nav and name in REQUIRED_FILES:
            report.error(name, f"pack nav missing links: {', '.join(missing_nav)}")

        if name in REQUIRED_FILES and html.count('class="active"') != 1:
            report.warn(name, "expected exactly one nav link marked active")


def check_glossary_coverage(files: dict[str, str], report: Report) -> None:
    if "slides.html" not in files or "glossary.html" not in files:
        return
    slide_terms = {
        a
        for a in ACRONYM_RE.findall(visible_text(files["slides.html"]))
        if a not in ACRONYM_STOPLIST
    }
    glossary_text = visible_text(files["glossary.html"]).upper()
    missing = sorted(t for t in slide_terms if t not in glossary_text)
    if missing:
        report.error(
            "glossary.html",
            f"acronyms used on slides but never defined: {', '.join(missing)}",
        )


def check_citations(files: dict[str, str], pages: list[str] | None, report: Report) -> int:
    total = 0
    for name, html in files.items():
        for raw in FROM_PAPER_RE.findall(html):
            total += 1
            claim = visible_text(raw)
            claim = re.sub(r"^\s*From the paper:\s*", "", claim, flags=re.I)

            match = PAGE_ANCHOR_RE.search(claim)
            if not match:
                report.error(name, f'claim has no page anchor: "{claim[:70]}..."')
                continue
            if pages is None:
                continue

            start = int(match.group(1))
            end = int(match.group(2) or start)
            if start < 1 or end > len(pages):
                report.error(
                    name, f"claim cites p.{start}-{end} but PDF has {len(pages)} pages"
                )
                continue

            # Allow a page of slack: PDF page breaks rarely align with ideas.
            lo, hi = max(1, start - 1), min(len(pages), end + 1)
            source = " ".join(pages[lo - 1 : hi])
            source_words = content_words(source)
            source_flat = normalize_for_search(source)

            body = SECTION_ANCHOR_RE.sub(" ", PAGE_ANCHOR_RE.sub(" ", claim))
            claim_words = content_words(body)
            if claim_words:
                overlap = len(claim_words & source_words) / len(claim_words)
                if overlap < 0.30:
                    report.error(
                        name,
                        f'claim is not supported by p.{start}-{end} '
                        f'(only {overlap:.0%} of terms appear there): "{body[:70]}..."',
                    )
                elif overlap < 0.55:
                    report.warn(
                        name,
                        f'claim only loosely matches p.{start}-{end} '
                        f'({overlap:.0%} of terms): "{body[:70]}..."',
                    )

            unmatched = [
                n
                for n in NUMBER_RE.findall(body)
                if len(n) > 1 and normalize_for_search(n) not in source_flat
            ]
            if unmatched:
                report.error(
                    name,
                    f"figures {', '.join(unmatched)} do not appear on p.{start}-{end}: "
                    f'"{body[:70]}..."',
                )
    return total


def validate(pack: Path, pdf: Path | None) -> tuple[Report, int]:
    report = Report()
    files: dict[str, str] = {}

    for name in REQUIRED_FILES:
        path = pack / name
        if not path.exists():
            report.error(pack.name, f"missing deliverable {name}")
            continue
        files[name] = path.read_text(encoding="utf-8")

    pages: list[str] | None = None
    if pdf is not None:
        sys.path.insert(0, str(Path(__file__).parent))
        from extract_sections import load_pages  # noqa: PLC0415
        from pypdf import PdfReader  # noqa: PLC0415

        pages = load_pages(PdfReader(str(pdf)))

    check_structure(pack, files, report)
    check_glossary_coverage(files, report)
    citations = check_citations(files, pages, report)
    return report, citations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path, help="Path to examples/<slug>/")
    parser.add_argument("--pdf", type=Path, help="Source PDF; enables citation grounding")
    args = parser.parse_args()

    if not args.pack.is_dir():
        print(f"Not a directory: {args.pack}", file=sys.stderr)
        sys.exit(2)

    report, citations = validate(args.pack, args.pdf)

    print(f"{args.pack}")
    for message in report.errors:
        print(f"  ERROR  {message}")
    for message in report.warnings:
        print(f"  WARN   {message}")

    grounded = "grounded against PDF" if args.pdf else "structure only (pass --pdf to verify claims)"
    print(f"  {citations} citations checked, {grounded}")

    if report.errors:
        print(f"  FAIL — {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        sys.exit(1)
    print(f"  PASS — 0 errors, {len(report.warnings)} warning(s)")


if __name__ == "__main__":
    main()
