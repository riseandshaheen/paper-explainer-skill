# paper-explainer-skill

Turn research PDFs into visual explainers — slides, deep dives, worked examples, and glossaries. Built for curious readers who want the big picture first, then depth on demand.

Works with **any coding agent** (Cursor, Claude Code, Copilot, etc.). Drop a PDF, point your agent at [AGENTS.md](AGENTS.md), and get a linked **paper pack**.

After you publish this repo and enable [GitHub Pages](https://docs.github.com/en/pages) (Settings → Pages → Deploy from `main` / root), examples will be live at:

`https://<your-username>.github.io/paper-explainer-skill/examples/<slug>/slides.html`

## What's in a paper pack

Each paper gets four HTML pages, cross-linked via a top nav bar:

| Deliverable | Time | Purpose |
|-------------|------|---------|
| **Slides** | ~3 min | 9-slide visual overview — minimal text, max graphics |
| **Deep dives** | ~15 min | Section-by-section explanations with diagrams |
| **Worked example** | ~5 min | One concrete instance traced through the method |
| **Glossary** | lookup | Flip cards — click a term for definition + analogy |

## Examples included

| Paper | Slides |
|-------|--------|
| [Word2Vec](examples/word2vec/1301.3781v3.pdf) (Mikolov et al., 2013) | [examples/word2vec/slides.html](examples/word2vec/slides.html) |
| [Permissionless Refereed Tournaments](examples/refereed-tournaments/2212.12439v1.pdf) (Nehab & Teixeira, 2022) | [examples/refereed-tournaments/slides.html](examples/refereed-tournaments/slides.html) |

Open any slide file in your browser, then use the nav bar to jump between deliverables.

## Project structure

```
paper-explainer-skill/
├── README.md
├── AGENTS.md                      # Instructions for coding agents
│
├── examples/                      # Paper packs (PDF + explainers)
│   ├── word2vec/
│   │   ├── 1301.3781v3.pdf        # Source paper
│   │   ├── slides.html
│   │   ├── deep.html
│   │   ├── worked.html
│   │   └── glossary.html
│   └── refereed-tournaments/
│       └── …
│
└── skills/read-research-paper/
    ├── SKILL.md                   # Full agent workflow (Steps 1–7)
    ├── scripts/
    │   ├── check_pdf.sh           # PDF readability gate
    │   ├── extract_outline.sh     # Title, abstract, headings
    │   ├── extract_sections.sh    # Per-section text with page numbers
    │   └── validate_pack.sh       # Pack + citation grounding check
    └── templates/
        ├── paper-deck.*           # Slide deck shell + CSS + JS
        ├── paper-pages.css        # Styles for deep dives, worked, glossary
        ├── glossary.js            # Flip-card interaction
        └── *.template.md          # Schemas for each deliverable
```

## Quick start

### With a coding agent

1. Clone this repo and open it in your editor.
2. Add a PDF under `examples/<slug>/` (create the folder if needed).
3. Tell your agent:

   > Read `@your-paper.pdf` using the workflow in AGENTS.md

The agent checks the PDF, extracts structure, and generates all four deliverables.

**Agent setup by tool:**

| Tool | How to wire it in |
|------|-------------------|
| **Cursor** | Skill auto-discovered via symlink at `.cursor/skills/read-research-paper/` |
| **Claude Code** | Add `AGENTS.md` to context, or: `claude --add-dir .` |
| **GitHub Copilot** | Reference `AGENTS.md` in a Copilot instruction file |
| **Windsurf / others** | Point the agent at `AGENTS.md` or `skills/read-research-paper/SKILL.md` |

No IDE-specific config is required — the workflow is plain Markdown + shell scripts.

### Manual — check a PDF

Scripts bootstrap a local Python venv on first run:

```bash
# Is the PDF readable?
skills/read-research-paper/scripts/check_pdf.sh path/to/paper.pdf

# Extract title, abstract, section headings
skills/read-research-paper/scripts/extract_outline.sh path/to/paper.pdf

# Extract each section's prose, tagged with page numbers
skills/read-research-paper/scripts/extract_sections.sh path/to/paper.pdf --text
```

Verdicts: `READABLE` (proceed) · `PARTIAL` (warn, proceed cautiously) · `UNREADABLE` (needs OCR or a text-based PDF).

### Manual — check a pack

```bash
skills/read-research-paper/scripts/validate_pack.sh examples/word2vec/ --pdf examples/word2vec/1301.3781v3.pdf
```

Verifies structure (placeholders, nav, anchors, glossary coverage) and — with `--pdf` — that
every `From the paper:` claim is supported by the page it cites. Exits non-zero on failure.

### Manual — view outputs

Open any HTML file directly in a browser — no build step, no server:

```bash
open examples/word2vec/slides.html
```

Slides use arrow keys or click left/right to navigate.

## Adding a new paper

1. Place the PDF in `examples/<slug>/` (create the folder if needed).
2. Ask your coding agent to read it (see [AGENTS.md](AGENTS.md)), **or** follow the schemas in `skills/read-research-paper/templates/`.
3. Explainers land alongside the PDF — four HTML files per pack.

```
Step 1  Confirm PDF is readable
Step 2  Read the paper's actual text (grounding gate)
Step 3  9-slide deck           → examples/<slug>/slides.html
Step 4  Sectional deep dives    → examples/<slug>/deep.html
Step 5  Worked example          → examples/<slug>/worked.html
Step 6  Glossary                → examples/<slug>/glossary.html
Step 7  Validate the pack       (must pass before delivery)
```

## Design principles

- **Grounded, not recalled** — explanations come from extracted text, and every claim cites a
  page that a validator checks. Famous papers are the risky case: an agent's recall is fluent
  and quietly wrong
- **Visual first** — diagrams and icons over walls of text
- **Plain language** — jargon gets defined or removed; simplify wording, never the facts
- **Same template, every paper** — 9 slides, same narrative arc (hook → gap → idea → method → results → impact)
- **Progressive depth** — slides for orientation, deep dives for comprehension, glossary for lookup

## Requirements

- **Python 3** (for PDF scripts — venv auto-created in `skills/read-research-paper/scripts/.venv`)
- **Any modern browser** (to view HTML outputs)
- **Any coding agent** (optional — for automated generation)

## License

Source papers retain their original licenses (arXiv). Explainer HTML and tooling in this repo are provided as-is for learning.
