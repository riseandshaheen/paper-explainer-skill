#!/usr/bin/env python3
"""Fast readability check for research PDFs. Samples pages; does not extract full text."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print(
        json.dumps(
            {
                "verdict": "ERROR",
                "reason": "pypdf not installed. Run scripts/check_pdf.sh instead.",
            },
            indent=2,
        )
    )
    sys.exit(2)

# Tune these as we learn from real papers
MIN_CHARS_PER_SAMPLED_PAGE = 80
MIN_ALNUM_RATIO = 0.45
MIN_READABLE_PAGES_RATIO = 0.67  # 2 of 3 sampled pages must pass


def sample_page_indices(page_count: int) -> list[int]:
    if page_count <= 0:
        return []
    if page_count == 1:
        return [0]
    if page_count == 2:
        return [0, 1]
    mid = page_count // 2
    return [0, mid, page_count - 1]


def text_quality(text: str) -> dict:
    stripped = text.strip()
    char_count = len(stripped)
    alnum = sum(1 for c in stripped if c.isalnum())
    ratio = alnum / char_count if char_count else 0.0
    has_abstract = bool(re.search(r"\babstract\b", stripped, re.I))
    has_references = bool(re.search(r"\breferences\b", stripped, re.I))
    return {
        "char_count": char_count,
        "alnum_ratio": round(ratio, 3),
        "has_abstract": has_abstract,
        "has_references": has_references,
        "readable": char_count >= MIN_CHARS_PER_SAMPLED_PAGE and ratio >= MIN_ALNUM_RATIO,
    }


def check_pdf(path: Path) -> dict:
    if not path.exists():
        return {"verdict": "UNREADABLE", "reason": "File not found", "path": str(path)}

    if path.suffix.lower() != ".pdf":
        return {"verdict": "UNREADABLE", "reason": "Not a .pdf file", "path": str(path)}

    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # noqa: BLE001 - surface any parse failure to user
        return {
            "verdict": "UNREADABLE",
            "reason": f"Could not open PDF: {exc}",
            "path": str(path),
        }

    if reader.is_encrypted:
        try:
            if reader.decrypt("") == 0:
                return {
                    "verdict": "UNREADABLE",
                    "reason": "PDF is password-protected",
                    "path": str(path),
                }
        except Exception:
            return {
                "verdict": "UNREADABLE",
                "reason": "PDF is encrypted and could not be decrypted",
                "path": str(path),
            }

    page_count = len(reader.pages)
    if page_count == 0:
        return {"verdict": "UNREADABLE", "reason": "PDF has no pages", "path": str(path)}

    samples: list[dict] = []
    for idx in sample_page_indices(page_count):
        try:
            text = reader.pages[idx].extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            text = ""
            samples.append(
                {
                    "page": idx + 1,
                    "error": str(exc),
                    "readable": False,
                }
            )
            continue

        quality = text_quality(text)
        preview = re.sub(r"\s+", " ", text.strip())[:200]
        samples.append({"page": idx + 1, "preview": preview, **quality})

    readable_pages = sum(1 for s in samples if s.get("readable"))
    readable_ratio = readable_pages / len(samples) if samples else 0.0
    any_abstract = any(s.get("has_abstract") for s in samples)
    any_references = any(s.get("has_references") for s in samples)

    if readable_ratio >= MIN_READABLE_PAGES_RATIO:
        verdict = "READABLE"
        reason = "Text extracts cleanly from sampled pages."
    elif readable_pages > 0:
        verdict = "PARTIAL"
        reason = (
            "Some pages have text, but quality is inconsistent. "
            "May be scanned, layout-heavy, or corrupted in places."
        )
    else:
        verdict = "UNREADABLE"
        reason = (
            "Almost no extractable text. Likely a scanned image PDF — OCR would be needed."
        )

    return {
        "verdict": verdict,
        "reason": reason,
        "path": str(path),
        "page_count": page_count,
        "sampled_pages": [s["page"] for s in samples],
        "readable_pages": readable_pages,
        "sample_count": len(samples),
        "signals": {
            "found_abstract": any_abstract,
            "found_references": any_references,
        },
        "samples": samples,
        "next_step": {
            "READABLE": "Proceed to Step 2: skim structure (title, abstract, sections).",
            "PARTIAL": "Tell the user extraction may be incomplete. Proceed cautiously or suggest OCR.",
            "UNREADABLE": "Stop. Ask the user for a text-based PDF or run OCR first.",
        }[verdict],
    }


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: check_pdf.py <path-to.pdf>", file=sys.stderr)
        sys.exit(1)

    result = check_pdf(Path(sys.argv[1]))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["verdict"] == "READABLE" else 1)


if __name__ == "__main__":
    main()
