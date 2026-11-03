---
name: earnings-summary
description: Summarize a company's most recent quarterly earnings for a given ticker — headline results vs consensus (beat/miss), segment and margin detail, forward guidance, and key messages from the earnings call (management commentary, guidance/outlook, and Q&A themes). Output is a medium-length (~3000 character) report. Use when asked to summarize the latest quarter, earnings report, or earnings call for a stock.
---

# Earnings Summary

Summarize the **most recent reported quarter** for a company given its ticker: the headline financials versus expectations, segment/margin detail, forward guidance, and the key messages from the earnings call.

## Input

A stock ticker symbol (e.g., NVDA, CRM, AVGO) provided by the caller.

If the caller does not specify a quarter, always summarize the **latest reported** quarter (the most recent earnings release), not the upcoming/unreported one.

## Research workflow

1. **Identify the quarter.** WebSearch for "{TICKER} latest quarterly earnings" to confirm which fiscal quarter most recently reported and the report date. State the quarter and date explicitly.
2. **Headline results vs consensus.** WebSearch for actual revenue and EPS versus analyst consensus estimates — determine the beat/miss magnitude for both. Note the stock's price reaction (after-hours or next-day move) if reported.
3. **Growth & profitability.** WebSearch for year-over-year revenue growth, gross/operating margin, and net income. Capture any sequential (QoQ) note if notable.
4. **Segments / key metrics.** WebSearch for the segment or product-line breakdown and the KPIs that matter for this company (e.g., cloud revenue, subscriber adds, data-center revenue, same-store sales). Pick the 2–4 most material.
5. **Forward guidance.** WebSearch for next-quarter and/or full-year guidance (revenue, EPS, margins) and whether it was raised, lowered, reaffirmed, or initiated versus prior guidance and versus consensus.
6. **Earnings call — key messages.** WebSearch for the earnings call transcript or recap. Extract:
   - **Management commentary:** CEO/CFO strategic priorities, notable statements, and overall tone (confident, cautious, defensive).
   - **Q&A themes:** what analysts pressed on and how management responded — often the real signal.
7. **Cross-check** headline numbers (revenue, EPS, guidance) against at least two independent sources before finalizing.

## Output requirements

- Total output should be **~3000 characters** (aim 2600–3400; hard cap 3600).
- Lead with a one-line verdict (beat/miss + tone).
- Use the section structure below. Bullets over prose. No markdown tables.
- Every figure must be traceable to the research — do not invent numbers. Use "N/A" or "not disclosed" when a figure isn't available rather than guessing.

## Response template

**{COMPANY NAME} ({TICKER}) — {Fiscal Quarter} Earnings** (reported {date}).

**Verdict:** {Beat/Miss/Mixed} on revenue and EPS; {stock reaction}. {One-line characterization of the quarter and management tone.}

**Headline Results:**
- Revenue: ${X}M/B, {+/-Y}% YoY — {beat/missed} consensus of ${Z} by {magnitude}.
- EPS: ${X} (GAAP/adj.) vs ${Z} consensus — {beat/miss} by {amount}.
- Net income: ${X}; gross margin {X}% ({+/- bps YoY}); operating margin {X}%.

**Segments / Key Metrics:**
- {Segment/KPI}: ${X}, {+/-Y}% YoY — {one-line note}.
- {Segment/KPI}: ${X}, {+/-Y}% YoY — {one-line note}.
- {Segment/KPI}: ${X}, {+/-Y}% YoY — {one-line note}.

**Guidance & Outlook:**
- Next quarter: revenue ${X}–${Y} ({raised/lowered/reaffirmed/initiated}; {vs consensus}).
- Full year: {revenue/EPS/margin guidance and change vs prior}.
- {One line on how guidance framed forward demand/headwinds.}

**Earnings Call — Key Messages:**
- Management: {CEO/CFO key message #1}.
- Management: {key message #2 — strategic priority, capital return, product cycle}.
- Tone: {confident / cautious / defensive} — {brief justification}.
- Q&A themes: analysts focused on {topic}; management {response/pushback}.

**Bottom line:** {1–2 sentence synthesis — what changed this quarter and the key debate going forward.}

## Formatting rules

- Use fiscal-quarter labels (e.g., "Q2 FY26"), and give the calendar report date.
- Revenue and income: use $M under $1B, $B at/above (one decimal, e.g., $8.3B). Use $T above $999B.
- EPS with two decimals; specify GAAP vs adjusted/non-GAAP (they differ — do not conflate).
- YoY / QoQ growth as a percentage with one decimal, signed (e.g., +12.4%, -3.1%).
- Margins as a percentage with one decimal; margin changes in basis points (e.g., +120 bps YoY).
- Beat/miss magnitude: give both the absolute gap and, where useful, the percent surprise.
- Guidance: always state the comparison — vs prior guidance AND vs consensus — and the direction (raised/lowered/reaffirmed).
- Attribute call quotes to a role (CEO/CFO), not a guessed name unless confirmed in the source.
- No line should exceed 140 characters; break at a natural point when needed.

## Final check

- Is the quarter the most recently REPORTED one, with an explicit report date?
- Are revenue AND EPS each shown vs consensus with a beat/miss call?
- Is at least one profitability figure (margin or net income) included?
- Are 2–4 material segments/KPIs included?
- Is forward guidance stated with direction vs prior AND vs consensus?
- Does the call section cover management commentary, tone, AND Q&A themes?
- Is GAAP vs adjusted EPS clearly labeled (not conflated)?
- Is total output ~3000 characters and within the hard cap?
- Are all figures cross-checked against 2+ sources, with "N/A" where unavailable?
