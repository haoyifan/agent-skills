---
name: ep-study
description: Use when researching why a stock gapped on a specific historical date — identifies the news catalyst behind the move (earnings, guidance, analyst action, M&A, FDA/clinical, product/contract, sector/macro sympathy, or none). Handles one or more dates per ticker. Useful for studying episodic pivot (EP) / Stockbee-style gap setups. Triggers: "what was the catalyst", "why did X gap on DATE", "research the catalyst for these dates".
---

# EP Study (Gap Catalyst Research)

Given a stock and one or more dates it gapped, identify the news catalyst behind each gap. The caller has already seen the gap on the chart — the job is to explain **what happened**, not to measure the move. Facts only: no gap-size/volume math, no EP-quality scoring.

## Input

A ticker plus one or more dates (e.g., `SMCI 2024-01-19` or `NVDA 2024-02-22, 2024-05-23, 2024-08-28`). Research each date **independently** and produce one card per date.

## Research workflow (repeat per date)

1. **Fix the news window.** The catalyst for a gap on date **D** almost always broke between the **prior session's after-hours close (D-1)** and **D's pre-market open**. Search that window first — that is what actually caused the gap.
2. **Search.** Run WebSearch queries such as:
   - `<company/ticker> <Month DD, YYYY>`
   - `<company> earnings <date>` (earnings is the most common EP catalyst — check it first)
   - `why did <company> stock jump/surge/gap <date>`
   - `<company> news <date>`
3. **Identify the primary catalyst** and classify it using the taxonomy below. If earnings: note beat/miss vs. estimates and guidance direction (raise/cut/reaffirm). Capture whether the news was a genuine **surprise** if the sources say so.
4. **Cross-check ≥2 sources** before stating the catalyst.
5. **No catalyst found is a valid result.** If nothing surfaces in the window, say so explicitly — a gap with no company news (technical breakout, sector sympathy, index flows) is itself a finding worth recording.

## Catalyst taxonomy

Used during research to frame the summary — **the label itself is not printed.**
Classify each gap as one of:

- **Earnings** — quarterly results (note beat/miss + guidance)
- **Guidance / pre-announcement** — standalone outlook or prelim results, no full print
- **Analyst action** — upgrade/downgrade, price-target change, new coverage
- **M&A / strategic** — acquisition, merger, takeover interest, buyback, spinoff, activist stake
- **Regulatory / clinical** — FDA action, trial data, legal/regulatory ruling
- **Product / business** — product launch, major contract/design win, partnership
- **Sector / macro / sympathy** — peer move, commodity/rate move, index inclusion, macro print
- **Other news** — anything credible that doesn't fit above
- **No clear catalyst found** — no company-specific news in the window

## Output — one card per date (chronological)

The card is pasted as a note onto a stock chart. Print **only** the bare date
header and a short catalyst summary — nothing else. Every line must be ≤ 80
characters wide; wrap the summary onto additional plain lines as needed.

```
<YYYY-MM-DD>
<factual summary of the catalyst, wrapped at 80 cols>
```

Do **not** print a "Catalyst:" label, the catalyst Type, Timing, Surprise, or
Sources. Classification, timing, and source cross-checking are done during
research (see workflow) to get the summary right — they are not shown. The
header is the date alone: no emoji, no ticker.

## Rules

- **Print only the date + summary.** No emoji, no ticker, no field labels, no
  Type/Timing/Surprise/Sources. Plain text pasted onto a chart.
- **80-column width.** No line exceeds 80 characters. Wrap the summary onto
  additional plain lines. Verify before returning (see final check).
- **Facts only.** Summarize what was announced. Do **not** estimate gap %, volume, or judge whether it was a "good" EP — the caller does that from the chart.
- **Attribute timing during research** (not in output): confirm the news broke after the prior close or pre-market that day, so the summary reflects the catalyst that actually caused *that* gap, not unrelated news.
- **Cross-check ≥2 dated sources during research** (not in output) before stating the catalyst. A recent article describing an old event is fine only if it states the date.
- Multiple dates → one card each, oldest to newest.
- Older dates (5+ years back) may have thin coverage — report what is found and flag low confidence rather than guessing.

## Final check

- One card per date, chronological?
- Header is the bare date — no emoji, no ticker?
- Only the date + catalyst summary printed (no label, Type, Timing, Surprise, Sources)?
- Catalyst verified against ≥2 dated sources during research (even if not printed)?
- If nothing found, summary reads "No clear catalyst found"?
- No gap-size/volume figures and no EP-quality scoring invented?
- **Every line ≤ 80 characters?**
