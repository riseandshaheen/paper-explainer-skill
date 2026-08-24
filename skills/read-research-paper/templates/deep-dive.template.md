# Deep dive section schema

One `section-block` per major paper section. Match `extract_outline.sh` headings.

## Per section

```html
<section class="section-block" id="{{slug}}">
  <div class="section-num">§{{NUMBER}} {{HEADING}}</div>
  <h2>{{PLAIN_TITLE}}</h2>           <!-- ≤8 words, no jargon -->
  <p class="plain">{{EXPLANATION}}</p> <!-- 2–4 short sentences -->
  <div class="visual">{{SVG_OR_DIAGRAM}}</div>
  <p class="from-paper"><strong>From the paper:</strong> {{ONE_SENTENCE_QUOTE_OR_PARAPHRASE}} (§{{NUMBER}}, p.{{PAGE}})</p>
</section>
```

## Rules

- 5–8 sections max (merge subsections if needed)
- Every section gets a visual — SVG with a `viewBox`
- "From the paper" ties claim to source; never paste abstract
- **Page anchor is required** on every `from-paper` line, and must be the page the
  claim actually came from in `extract_sections.sh` output
- Keep the paper's exact figures — `53.3%`, not "about half"
- TOC at top links to `#id` anchors

## Verify

```bash
skills/read-research-paper/scripts/validate_pack.sh examples/<slug>/ --pdf paper.pdf
```

## Output

`examples/<slug>/deep.html`
