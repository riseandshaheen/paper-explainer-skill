---
name: read-research-paper
description: >-
  Reads and explains research papers as a visual pack — HTML slides, sectional deep
  dives, worked examples, and glossaries. Use when the user shares a PDF paper,
  asks to understand or summarize a research paper, or wants slides explaining
  academic work.
---

# Read a Research Paper (Simple Mode)

Goal: deliver a **curious reader pack** — skim fast, then go deeper on demand.

After Step 1 passes, **do not ask permission** — build all deliverables automatically.

## Workflow

```
- [ ] Step 1: Confirm PDF is readable (gate)
- [ ] Step 2: Read the paper's actual text (grounding gate)
- [ ] Step 3: 9-slide HTML deck
- [ ] Step 4: Sectional deep dives
- [ ] Step 5: Worked example
- [ ] Step 6: Glossary flip cards
- [ ] Step 7: Validate the pack (gate)
```

All outputs go in **`examples/<slug>/`**, with same-folder pack nav: Slides · Deep dives · Worked example · Glossary.

---

## Step 1: Confirm the PDF is readable

**Do not** use the Read tool on raw `.pdf` files.

```bash
skills/read-research-paper/scripts/check_pdf.sh path/to/paper.pdf
```

| Verdict | Action |
|---------|--------|
| `READABLE` | Proceed — no user prompt |
| `PARTIAL` | Warn briefly, proceed with caveats |
| `UNREADABLE` | Stop. Ask for text PDF or OCR |

---

## Step 2: Read the paper (grounding gate)

**Never write an explanation from prior knowledge of the paper.** Famous papers are
the dangerous case: recall feels fluent and is often subtly wrong. Read the text.

```bash
skills/read-research-paper/scripts/extract_sections.sh path/to/paper.pdf --text
```

Returns every section's prose tagged with page numbers. Use `--section 3.2` for one
section, `--max-chars N` to widen or narrow each block.

Rules for the rest of the workflow:

- Every number, dataset name, and result must be copied from this output — never recalled.
- Every `From the paper:` line ends with a page anchor: `(§3.2, p.4)`.
- If the text does not support a claim, cut the claim. Do not fill the gap from memory.
- If `section_count` is 0, the layout is unusual — say so and work from `--text` output alone.

---

## Step 3: Slide deck

```bash
skills/read-research-paper/scripts/extract_outline.sh path/to/paper.pdf
```

Copy `templates/paper-deck.template.html` → `examples/<slug>/slides.html`.

Schema: [templates/SLIDE-SCHEMA.md](templates/SLIDE-SCHEMA.md)

Asset path from `examples/<slug>/`: `../../skills/read-research-paper/templates/`

---

## Step 4: Sectional deep dives

One HTML page, one block per major paper section.

**Schema:** [templates/deep-dive.template.md](templates/deep-dive.template.md)

```
examples/<slug>/deep.html
```

- Use `templates/paper-pages.css`
- TOC at top → anchor links
- 5–8 sections, merged from the Step 2 extraction
- Each section: plain explanation + visual + "From the paper" line with a page anchor

---

## Step 5: Worked example

Trace one concrete instance through the core method.

**Schema:** [templates/worked-example.template.md](templates/worked-example.template.md)

```
examples/<slug>/worked.html
```

- 5–8 numbered steps
- Real values from the Step 2 extraction (dims, window size, dataset) — never recalled
- Final step = payoff (result or famous trick)

---

## Step 6: Glossary

Flip cards for jargon — click to reveal definition + analogy.

**Schema:** [templates/glossary.template.md](templates/glossary.template.md)

```
examples/<slug>/glossary.html
```

- 12–20 terms from abstract + method sections
- Each card: term → definition (≤20 words) + analogy + section ref (§)
- Include `templates/glossary.js` for flip interaction
- Every acronym on the slides must appear here — Step 7 enforces this

---

## Step 7: Validate (gate)

```bash
skills/read-research-paper/scripts/validate_pack.sh examples/<slug>/ --pdf path/to/paper.pdf
```

Checks: unfilled placeholders, broken nav and anchors, `<svg>` without `viewBox`,
acronyms on slides missing from the glossary, and — the important one — whether each
`From the paper:` claim is actually supported by the page it cites.

**Do not deliver a failing pack.** Fix errors and re-run until it passes. Warnings are
judgement calls: a loose match may be a fair paraphrase, or may be drift.

| Failure | Usual cause |
|---------|-------------|
| `claim has no page anchor` | Missing `(§N, p.N)` on a `from-paper` line |
| `figures X do not appear on p.N` | A recalled statistic — re-read the section |
| `claim is not supported by p.N` | Wrong page cited, or the claim was invented |
| `acronyms used on slides but never defined` | Add the glossary cards |

---

## Pack nav (every file)

```html
<nav class="pack-nav">
  <span class="brand">{Paper title} pack</span>
  <a href="slides.html">Slides</a>
  <a href="deep.html">Deep dives</a>
  <a href="worked.html">Worked example</a>
  <a href="glossary.html">Glossary</a>
</nav>
```

Mark the current page with `class="active"` on its link.

---

## Deliver to user

```markdown
## Paper pack ready

| Deliverable | Open |
|-------------|------|
| Slides (3 min) | `examples/<slug>/slides.html` |
| Deep dives | `examples/<slug>/deep.html` |
| Worked example | `examples/<slug>/worked.html` |
| Glossary | `examples/<slug>/glossary.html` |

[One sentence on what the paper is about]
```

---

## Assets

| File | Purpose |
|------|---------|
| `templates/paper-deck.*` | 9-slide deck |
| `templates/paper-pages.css` | Deep dives, worked example, glossary |
| `templates/glossary.js` | Flip-card interaction |
| `templates/deep-dive.template.md` | Section block schema |
| `templates/worked-example.template.md` | Step-by-step schema |
| `templates/glossary.template.md` | Flip card schema |
| `examples/word2vec/` | Reference pack — grounded, passes validation |
| `examples/refereed-tournaments/` | Reference pack |

| Script | Purpose |
|--------|---------|
| `scripts/check_pdf.sh` | Readability gate (Step 1) |
| `scripts/extract_sections.sh` | Per-section text with page numbers (Step 2) |
| `scripts/extract_outline.sh` | Title, abstract, headings (Step 3) |
| `scripts/validate_pack.sh` | Pack + citation validation (Step 7) |

---

## Explanation style

- Short sentences. Define jargon once — or remove it.
- Analogies over definitions.
- If a concept needs more than 8 words, draw it instead.
- Simplify the wording, never the facts. Rounding "53.3%" to "over 50%" loses the citation.
