# Glossary schema

Flip cards for every jargon term a curious reader might hit.

## Per term

```html
<div class="glossary-card">
  <div class="card-inner">
    <div class="card-front">
      <span class="term">{{TERM}}</span>
      <span class="hint">click to flip</span>
    </div>
    <div class="card-back">
      <p class="def">{{PLAIN_DEFINITION}}</p>      <!-- 1 sentence, ≤20 words -->
      <p class="analogy">{{EVERYDAY_ANALOGY}}</p>   <!-- 1 sentence -->
      <span class="where">{{SECTION_REF}}</span>    <!-- e.g. §3.1 -->
    </div>
  </div>
</div>
```

## Rules

- 12–20 terms per paper (not every word — only barriers to understanding)
- Definition must not use other glossary terms; if unavoidable, define the simpler term first
- Every term gets an analogy
- `where` links term to paper section for cross-reference with deep dives
- Grid layout: `glossary-grid` in `paper-pages.css`
- Include `glossary.js` for click-to-flip

## How to pick terms

1. Scan abstract + method sections for capitalized acronyms and domain nouns
2. Include any term used in slides or worked example without definition
3. Skip terms defined inline in deep dives unless they're central (e.g. CBOW, Skip-gram)

## Output

`examples/<slug>/glossary.html`
