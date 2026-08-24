# Universal slide template (9 slides)

Every research paper maps to the same narrative arc. Fill each slot; skip or merge only when the paper truly has nothing for that slot.

| # | Type | Headline rule | Visual | Agent fills from paper |
|---|------|---------------|--------|------------------------|
| 1 | **cover** | Full title | Typography hero | Title, authors, year/venue |
| 2 | **hook** | ≤12 words | Problem → insight icons | Why anyone should care |
| 3 | **gap** | ≤10 words per side | Before / After panels | Old approach vs new approach |
| 4 | **idea** | ≤15 words | Big centered statement | The one contribution |
| 5 | **method** | 4 node labels, ≤4 words each | Horizontal flow | Input → process → output |
| 6 | **mechanism** | ≤20 word caption | Custom SVG diagram | Architecture, equation visual, or key trick |
| 7 | **evidence** | 3 numbers max | Stat cards + bar chart | Best result vs baseline |
| 8 | **impact** | ≤8 words × 3 | Emoji + short phrase | Real-world consequences |
| 9 | **close** | ≤20 words | Pull-quote style | One sentence to remember |

## Text budget (hard limits)

- **No slide** may have more than 40 words of body text total.
- **Slide 4 (idea)** is the only slide allowed a single long sentence.
- Prefer **diagrams, icons, numbers** over bullet lists.
- Never paste the abstract verbatim — rewrite for a smart 15-year-old.

## When to merge slides

| Situation | Action |
|-----------|--------|
| Pure theory paper, no experiments | Merge 7 into 6; show "prediction" instead of stats |
| Short 4-page paper | Drop slide 6; expand slide 5 diagram |
| Survey / review paper | Replace 5–6 with taxonomy diagram; slide 7 = "key papers table" as icons |
| Systems paper | Slide 6 = system architecture; slide 7 = latency/throughput stats |

## SVG guidelines for slide 6

Draw simple boxes-and-arrows. No screenshots from the PDF.

- ML model paper → layers / data flow
- Algorithm paper → step diagram
- Experiment paper → experimental setup pipeline
- Max 8 nodes in any diagram

## Output location

Save filled decks to: `examples/<slug>/slides.html`

Copy CSS/JS paths from template, or inline CSS for a fully portable single file.

## Quality check before delivering

- [ ] Could someone skim all 9 slides in under 3 minutes?
- [ ] Is every jargon term either gone or visually explained?
- [ ] Does slide 4 alone convey what the paper adds?
- [ ] Are the 3 stats on slide 7 the paper's strongest claims?
