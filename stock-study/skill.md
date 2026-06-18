# Stock Fundamental Research

Generate a comprehensive fundamental research PDF report for a given stock ticker.

## Input

A stock ticker symbol (e.g., AAPL, LLY, TER).

## Research workflow

Gather all data below via WebSearch. Cross-check financial figures against at least two sources.

### 1. Business overview
- Sector, business segments, key products/services, and main growth drivers (1-3 sentences)

### 2. Valuation metrics (6 items)
Search: "{Company} {TICKER} valuation P/E EV/EBITDA PEG ratio 2026"
- P/E (TTM), Forward P/E, P/S (TTM), EV/EBITDA, PEG Ratio, FCF Yield
- For each, also find the sector median to note if it trades at premium/discount

### 3. Quarterly financials (last 6 quarters)
Search: "{Company} {TICKER} quarterly earnings revenue EPS 2025 2026"
- For each quarter: label (e.g. "Q1 FY26"), revenue, diluted EPS, YoY revenue growth %
- Use GAAP EPS unless GAAP is heavily distorted by one-time items — then use adjusted EPS and note it

### 4. Balance sheet health (6 items)
Search: "{Company} {TICKER} balance sheet debt cash current ratio 2025 2026"
- Total Debt, Net Debt/EBITDA, Interest Coverage, Current Ratio, Cash & Equivalents, Debt/Equity

### 5. Profitability & margins (6 items)
Search: "{Company} {TICKER} gross margin operating margin net margin ROE ROIC"
- Gross Margin, Operating Margin, Net Margin, ROE, ROIC, Asset Turnover

### 6. Cash flow (6 items)
Search: "{Company} {TICKER} operating cash flow free cash flow capex dividends buybacks"
- Op. Cash Flow (TTM), Free Cash Flow (TTM), Capex (TTM), FCF Margin, Div. Yield / Payout Ratio, Buybacks (TTM)

### 7. Growth profile (6 items)
Search: "{Company} {TICKER} revenue EPS growth CAGR estimates consensus 2026 2027"
- Rev CAGR (3Y), EPS CAGR (3Y), Next Q Est. Revenue, Next Q Est. EPS, FY Est. Revenue (current), FY Est. Revenue (next)

### 8. Ownership & sentiment (4 items)
Search: "{Company} {TICKER} institutional ownership insider buying short interest"
- Institutional Ownership %, Insider Ownership %, Recent Insider Activity, Short Interest %

### 9. Analyst consensus (4 items)
Search: "{Company} {TICKER} analyst price target rating consensus"
- Consensus Rating, Mean Price Target, # Buy/Hold/Sell, vs Current Price

### 10. Risks & catalysts
Search: "{Company} {TICKER} risks catalysts upcoming events 2026"
- 2-4 sentences covering key risks and near-term catalysts (earnings dates, product launches, regulatory, macro)

## Output — PDF generation

After gathering all data, write a JSON file to `/tmp/{TICKER}_data.json` with the following structure, then run the PDF generator script.

### JSON schema

```json
{
  "company_name": "Full Company Name",
  "ticker": "TICK",
  "sector": "Sector / Industry",
  "date": "YYYY-MM-DD",
  "business_overview": "1-3 sentence overview...",
  "valuation": [
    ["P/E (TTM)", "25.3x"],
    ["Fwd P/E", "21.1x"],
    ["P/S (TTM)", "5.2x"],
    ["EV/EBITDA", "18.4x"],
    ["PEG Ratio", "1.5x"],
    ["FCF Yield", "3.2%"]
  ],
  "quarterly_financials": [
    ["Q1 FY26", "$5.2B", "$1.45", "+12.3%"],
    ["Q4 FY25", "$4.8B", "$1.32", "+8.7%"],
    ["...6 rows total, most recent first..."]
  ],
  "balance_sheet": [
    ["Total Debt", "$12.5B"],
    ["Net Debt/EBITDA", "1.8x"],
    ["Interest Coverage", "12.3x"],
    ["Current Ratio", "1.5x"],
    ["Cash & Equiv.", "$4.2B"],
    ["Debt/Equity", "1.2x"]
  ],
  "profitability": [
    ["Gross Margin", "65.2%"],
    ["Op. Margin", "28.4%"],
    ["Net Margin", "21.3%"],
    ["ROE", "35.2%"],
    ["ROIC", "18.7%"],
    ["Asset Turnover", "0.8x"]
  ],
  "cash_flow": [
    ["Op. Cash Flow", "$8.3B"],
    ["Free Cash Flow", "$6.1B"],
    ["Capex", "$2.2B"],
    ["FCF Margin", "24.5%"],
    ["Div Yield / Payout", "1.2% / 32%"],
    ["Buybacks (TTM)", "$3.5B"]
  ],
  "growth": [
    ["Rev CAGR (3Y)", "+15.2%"],
    ["EPS CAGR (3Y)", "+22.8%"],
    ["Next Q Est. Rev", "$5.5B"],
    ["Next Q Est. EPS", "$1.52"],
    ["FY26 Est. Rev", "$21.2B"],
    ["FY27 Est. Rev", "$24.8B"]
  ],
  "ownership": [
    ["Inst. Ownership", "82.5%"],
    ["Insider Ownership", "1.3%"],
    ["Insider Activity", "Net buying"],
    ["Short Interest", "2.1%"]
  ],
  "analyst_consensus": [
    ["Rating", "Overweight"],
    ["Mean Target", "$185"],
    ["Buy / Hold / Sell", "22 / 8 / 2"],
    ["Current Price", "$162"]
  ],
  "risks_catalysts": "2-4 sentences on key risks and catalysts..."
}
```

### Formatting rules for JSON values

- Revenue: use appropriate unit — "$X.XB" for billions, "$X.XM" for millions
- EPS: two decimal places with dollar sign, e.g. "$1.45" or "-$0.21"
- Ratios: one decimal with "x" suffix, e.g. "18.4x"
- Percentages: one decimal with "%" suffix, e.g. "+12.3%" or "-5.1%"
- Prefix positive growth with "+", negative with "-"
- If a value is unavailable after searching, use "N/A"

### Generate the PDF

```bash
source ~/stock-study/.venv/bin/activate && python3 /Users/pringles/.claude/skills/stock-study/generate_pdf.py /tmp/{TICKER}_data.json
```

The script outputs the PDF path. Send the PDF file to the user with SendUserFile after generation.

## Final checks

- Did you cross-check financials against 2+ sources?
- Are all 10 sections populated (or marked N/A where data is truly unavailable)?
- Is the JSON valid before running the script?
- Did the PDF generate successfully and get sent to the user?
