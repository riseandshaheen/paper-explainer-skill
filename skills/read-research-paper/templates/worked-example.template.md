# Worked example schema

Trace **one concrete instance** through the paper's core method. 5–8 numbered steps.

## Pick the example

| Paper type | Example to trace |
|------------|------------------|
| ML model | One training sample through forward pass |
| Algorithm | One input through each step |
| System | One request through the pipeline |
| Experiment | One test case and how it's scored |

## Per step

```html
<div class="step">
  <div class="step-num">{{N}}</div>
  <div class="step-body">
    <h3>{{STEP_TITLE}}</h3>           <!-- ≤6 words -->
    <p>{{WHAT_HAPPENS}}</p>            <!-- 1–2 sentences -->
    <div class="highlight-box">{{CONCRETE_VALUES}}</div>  <!-- optional -->
    <div class="visual">{{DIAGRAM}}</div>                 <!-- optional -->
    <p class="from-paper"><strong>From the paper:</strong> {{SOURCE}} (§{{N}}, p.{{PAGE}})</p>
  </div>
</div>
```

## Rules

- Use real values from `extract_sections.sh` (dimensions, window size, dataset name) — never recalled
- Any step asserting a paper value carries a `from-paper` line with a page anchor
- Trace the example **the paper itself** uses; if you substitute a friendlier one, say so
  and cite where the paper's version lives
- Last step = payoff (result, analogy, or "what you get at the end")
- No math beyond one equation in the final step

## Output

`examples/<slug>/worked.html`

## Verify

```bash
skills/read-research-paper/scripts/validate_pack.sh examples/<slug>/ --pdf paper.pdf
```
