---
name: stock-summary
description: Generate a concise stock summary for a given ticker — business overview, six quarterly results with revenue consensus and beat/miss, and valuation. Output is kept under 1100 characters for easy pasting. Use when asked for a quick stock profile or summary.
---

# Stock Summary

Generate a concise summary of a stock given its ticker symbol.

## Input

A stock ticker symbol (e.g., VIAV, AAPL, MSFT) provided by the caller.

## Research workflow

1. **Business overview:** WebSearch for the company's sector, business segments, and key products/services.
2. **Financial data:** WebSearch for the most recent 6 quarterly results —
   reported revenue, the pre-release consensus revenue estimate, revenue
   beat/miss, EPS, and year-over-year revenue growth percentage. For each
   quarter, use the consensus estimate available immediately before the report,
   not a subsequently revised estimate.
3. **Valuation:** WebSearch for the current trailing P/E ratio, forward P/E ratio, PEG ratio (P/E to growth), trailing P/S (price-to-sales) ratio, and market capitalization.
4. **Ownership:** WebSearch for the current institutional ownership as a percentage of shares outstanding.
5. Cross-check at least two sources to confirm the financial figures.

## Output requirements

- Total output must be **under 1100 characters**.
- Three sections: business overview, quarterly financials, and valuation.
- No markdown tables — use a bullet list for quarterly data, sorted **oldest to newest** (earliest quarter first).

## Response template

**{COMPANY NAME} ({TICKER})** — {Sector}.

{1-2 sentence business overview covering segments and key products/growth drivers.}

**Quarterly Financials:**

- {Q label}: ${rev} rev vs ${est} est, +${beat} (+{X}%) beat, ${EPS} EPS, +{Y}% YoY
- {Q label}: ${rev} rev vs ${est} est, -${miss} (-{X}%) miss, ${EPS} EPS, +{Y}% YoY
- {Q label}: ${rev} rev vs ${est} est, +${beat} (+{X}%) beat, ${EPS} EPS, +{Y}% YoY
- {Q label}: ${rev} rev vs ${est} est, +${beat} (+{X}%) beat, ${EPS} EPS, +{Y}% YoY
- {Q label}: ${rev} rev vs ${est} est, +${beat} (+{X}%) beat, ${EPS} EPS, +{Y}% YoY
- {Q label}: ${rev} rev vs ${est} est, +${beat} (+{X}%) beat, ${EPS} EPS, +{Y}% YoY

**Valuation:** Trailing P/E: {X.X} | Forward P/E: {X.X} | PEG: {X.X} | P/S: {X.X} | MCap: {$X.XB}

**Institutional Ownership:** {XX.X}%

{1-2 sentence trend summary.}

## Formatting rules

- Use fiscal year quarter labels (e.g., "Q3 FY26").
- Revenue in millions with one decimal (e.g., $406.8M).
- Show the pre-release revenue estimate in millions with one decimal. Show the
  revenue beat/miss as both a dollar amount and percentage of the estimate,
  e.g. `+$42.1M (+6.3%) beat` or `-$8.4M (-2.1%) miss`. If no reliable
  pre-release estimate is available, use `N/A` for both estimate and beat/miss.
- EPS with two decimals, include sign (e.g., $0.03, -$0.21).
- YoY growth as percentage with one decimal (e.g., +42.8%).
- Negative EPS or negative YoY growth should show a minus sign.
- P/E ratios with one decimal. Use "N/A" if the company is unprofitable (negative trailing EPS).
- PEG ratio with one decimal. Use "N/A" if trailing P/E is N/A or earnings growth is negative.
- P/S ratio with one decimal (trailing twelve months).
- Market cap in billions with one decimal (e.g., $45.2B). Use trillions if over $999B (e.g., $1.2T).
- Institutional ownership as a percentage with one decimal (e.g., 78.4%). Use "N/A" if not available. Cap the displayed value at 100.0% if a source reports over 100% (float-based quirk).
- No line may exceed **140 characters**. Insert a line break at a natural point (after a comma, period, or between clauses) when a line would be too long.

## Final check

- Is the output under 1100 characters?
- Are there exactly 6 quarters of data?
- Does each quarter line include reported revenue, pre-release expected revenue,
  revenue beat/miss, EPS, and YoY growth?
- Is the business overview concise (1-2 sentences max)?
- Are trailing P/E, forward P/E, PEG, P/S, and market cap included?
- Is institutional ownership (percentage) included?
- Is every line 140 characters or fewer?
