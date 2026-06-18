---
name: stock-summary
description: Generate a concise stock summary for a given ticker — business overview (sector, segments, products), recent quarterly financials (revenue, EPS, YoY revenue growth), and valuation (trailing & forward P/E, P/S). Output is kept under 1100 characters for easy pasting. Use when asked for a quick stock profile or summary.
---

# Stock Summary

Generate a concise summary of a stock given its ticker symbol.

## Input

A stock ticker symbol (e.g., VIAV, AAPL, MSFT) provided by the caller.

## Research workflow

1. **Business overview:** WebSearch for the company's sector, business segments, and key products/services.
2. **Financial data:** WebSearch for the most recent 6 quarterly results — revenue, EPS, and year-over-year revenue growth percentage.
3. **Valuation:** WebSearch for the current trailing P/E ratio, forward P/E ratio, and trailing P/S (price-to-sales) ratio.
4. Cross-check at least two sources to confirm the financial figures.

## Output requirements

- Total output must be **under 1100 characters**.
- Three sections: business overview, quarterly financials, and valuation.
- No markdown tables — use a bullet list for quarterly data, sorted **oldest to newest** (earliest quarter first).

## Response template

**{COMPANY NAME} ({TICKER})** — {Sector}.

{1-2 sentence business overview covering segments and key products/growth drivers.}

**Quarterly Financials:**

- {Q label}: ${rev} rev, ${EPS} EPS, +{X}% YoY
- {Q label}: ${rev} rev, ${EPS} EPS, +{X}% YoY
- {Q label}: ${rev} rev, ${EPS} EPS, +{X}% YoY
- {Q label}: ${rev} rev, ${EPS} EPS, +{X}% YoY
- {Q label}: ${rev} rev, ${EPS} EPS, +{X}% YoY
- {Q label}: ${rev} rev, ${EPS} EPS, +{X}% YoY

**Valuation ({YYYY-MM-DD}):** Trailing P/E: {X.X} | Forward P/E: {X.X} | P/S: {X.X}

{1-2 sentence trend summary.}

## Formatting rules

- Use fiscal year quarter labels (e.g., "Q3 FY26").
- Revenue in millions with one decimal (e.g., $406.8M).
- EPS with two decimals, include sign (e.g., $0.03, -$0.21).
- YoY growth as percentage with one decimal (e.g., +42.8%).
- Negative EPS or negative YoY growth should show a minus sign.
- P/E ratios with one decimal. Use "N/A" if the company is unprofitable (negative trailing EPS).
- P/S ratio with one decimal (trailing twelve months).
- No line may exceed **140 characters**. Insert a line break at a natural point (after a comma, period, or between clauses) when a line would be too long.

## Final check

- Is the output under 1100 characters?
- Are there exactly 6 quarters of data?
- Does each quarter line include revenue, EPS, and YoY growth?
- Is the business overview concise (1-2 sentences max)?
- Are trailing P/E, forward P/E, and P/S ratios included?
- Is every line 140 characters or fewer?
