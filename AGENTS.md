# Agent instructions

Repo: **paper-explainer-skill** — visual paper packs for coding agents.

When the user asks to read, explain, or summarize a research paper PDF in this repo, follow the workflow in [skills/read-research-paper/SKILL.md](skills/read-research-paper/SKILL.md).

## Trigger phrases

- "Read this paper"
- "Explain `@paper.pdf`"
- "Generate a paper pack for …"
- Any request to understand or summarize a PDF in this project

## What to produce

For each paper, generate four linked HTML files in one folder:

| Output | Path |
|--------|------|
| Slides | `examples/<slug>/slides.html` |
| Deep dives | `examples/<slug>/deep.html` |
| Worked example | `examples/<slug>/worked.html` |
| Glossary | `examples/<slug>/glossary.html` |

## First commands to run

```bash
skills/read-research-paper/scripts/check_pdf.sh path/to/paper.pdf
skills/read-research-paper/scripts/extract_sections.sh path/to/paper.pdf --text
```

If the PDF verdict is `UNREADABLE`, stop and tell the user.

## Last command to run

```bash
skills/read-research-paper/scripts/validate_pack.sh examples/<slug>/ --pdf examples/<slug>/paper.pdf
```

Never deliver a pack that fails validation.

## Key rules

- Do **not** read raw `.pdf` files with a text editor — use the scripts above
- **Write only from extracted text, never from prior knowledge of the paper.** Well-known
  papers are the risky case: recall is fluent and quietly wrong
- Every `From the paper:` line carries a page anchor — `(§3.2, p.4)`
- After a `READABLE` verdict, build all four deliverables without asking permission
- Use templates and schemas in `skills/read-research-paper/templates/`
- Template assets path from output HTML: `../../skills/read-research-paper/templates/`
- Pack nav links are same-folder: `slides.html`, `deep.html`, `worked.html`, `glossary.html`

## Full workflow

See [skills/read-research-paper/SKILL.md](skills/read-research-paper/SKILL.md) for the complete 7-step process, schemas, and style guide.
