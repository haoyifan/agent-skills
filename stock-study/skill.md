# Stock Fundamental Research

Generate a comprehensive fundamental research PDF report for a given stock ticker.

## Input

A stock ticker symbol (e.g., AAPL, LLY, TER).

## Research workflow

Gather all data below via WebSearch. Cross-check financial figures against at least two sources.

### 1. Business overview
- Sector and high-level business model (2-3 sentences)
- Do NOT cram product detail here — that belongs in section 2

### 2. Business segments & product lines (required)

This is the most important qualitative section. A consolidated financial table alone is insufficient for multi-line businesses (e.g., Google, Amazon) and still too thin for simpler companies (e.g., Vita Coco's brand portfolio).

**Identify segments using this priority:**
1. Segments exactly as reported in the latest 10-K / earnings release / investor deck
2. If not formally segmented, break down by **brand, product category, geography, or channel** — whichever the company emphasizes
3. Cover every material line (>5% of revenue, or strategically important even if smaller)

**Search patterns:**
- `"{Company} {TICKER} segment revenue operating income breakdown 2025 2026"`
- `"{Company} earnings supplement segment results"`
- `"{Company} investor presentation segment revenue margin"`
- For each major product: `"{Product/Brand} revenue growth market share 2026"`

**Per segment / product line, gather:**

| Field | Notes |
|-------|-------|
| Revenue | Latest FY or TTM; use segment disclosure when available |
| % of total | Share of consolidated revenue |
| YoY growth | Segment revenue growth rate |
| Margin | Operating margin preferred; gross margin if that's all that's disclosed |
| Key products | 1-line list of main products/services/brands in this line |
| Outlook | 2-4 sentences: growth drivers, competitive position, margin trajectory, key risks |

If a company does not disclose segment margins, say so explicitly and substitute qualitative profitability (e.g., "estimated high-margin cash cow" or "investment-stage, likely loss-making") with a source or rationale.

**Cross-check** segment revenue figures against the consolidated total — they should reconcile (allow minor rounding / eliminations).

### 3. Competitors & industry landscape (required)

Map the competitive set and explain how the subject company fits.

**Search patterns:**
- `"{Company} {TICKER} competitors market share industry landscape 2026"`
- `"{Industry/category} market size growth rate 2026"`
- `"{Competitor} vs {Company} comparison revenue market share"`
- 10-K "Competition" section and earnings-call commentary

**Gather:**
- **Industry overview** (2-3 sentences): market size, growth rate, maturity (fragmented vs consolidated), key structural trends
- **Competitor comparison table** (4-8 peers): direct and adjacent competitors, including private labels / platform players where relevant
- **Competitive assessment** (2-4 sentences): how the company ranks on share, growth, margins, differentiation, and strategic threats/opportunities

**Per competitor row, include:**

| Column | Notes |
|--------|-------|
| Competitor | Company name (private label as a group if relevant) |
| Scale | Revenue, market cap, or category sales if exact revenue unavailable |
| Market share | Category share if available; else "N/A" |
| Key strength | Primary competitive advantage |
| vs {TICKER} | One-line relative comparison (e.g., "Larger but slower-growing") |

Include the subject company as the first row in `competitor_summary` for easy side-by-side reference.

### 4. Customers & value chain (required)

Identify who the company sells to and who it depends on upstream/downstream.

**Search patterns:**
- `"{Company} {TICKER} major customers top clients revenue concentration 10-K"`
- `"{Company} suppliers manufacturing partners supply chain"`
- `"{Company} distribution channels retail partners wholesalers"`
- 10-K customer concentration disclosure (e.g., ">10% customer")

**Gather:**
- **Value chain overview** (1-2 sentences): how the company sits in the industry value chain
- **Major customers / clients** (3-6 rows): named customers or channel types; include % of revenue if disclosed in filings
- **Upstream** (3-5 rows): key inputs, suppliers, contract manufacturers, technology/licence providers, labor/geography dependencies
- **Downstream** (3-5 rows): distributors, retailers, platforms, resellers, end-market channels
- **Value chain assessment** (2-4 sentences): concentration risk, bargaining power, supply-chain vulnerabilities, channel mix

**Per value-chain row:**

| Column | Notes |
|--------|-------|
| Category | Input type, customer, or channel |
| Key companies | Named players (e.g., Walmart, Costco, Foxconn) or "Fragmented farmers" |
| Role / notes | What they provide or buy; dependency level; % revenue if known |

If exact customer names are not disclosed, use channel types (e.g., "Mass retail", "Club stores", "E-commerce") and note the disclosure limitation.

### 5. Valuation metrics (6 items)
Search: "{Company} {TICKER} valuation P/E EV/EBITDA PEG ratio 2026"
- P/E (TTM), Forward P/E, P/S (TTM), EV/EBITDA, PEG Ratio, FCF Yield
- For each, also find the sector median to note if it trades at premium/discount

### 6. Annual & quarterly financials

**Annual (last 5 fiscal years, most recent first)**

Search: `"{Company} {TICKER} annual revenue net income EPS fiscal year 2022 2023 2024 2025"`

For each fiscal year: label (e.g. "FY2025"), revenue, diluted EPS, YoY revenue growth %, YoY EPS growth %

- Use GAAP EPS unless GAAP is heavily distorted by one-time items — then use adjusted EPS and note it
- YoY EPS growth compares to the prior fiscal year's EPS (not quarterly annualized)

**Quarterly (last 6 quarters, most recent first)**

Search: `"{Company} {TICKER} quarterly earnings revenue EPS 2025 2026"`

For each quarter: label (e.g. "Q1 FY26"), revenue, diluted EPS, YoY revenue growth %

- Same GAAP/adjusted EPS rule as annual
- Quarterly table does not need EPS growth column (YoY rev % is sufficient)

### 7. Balance sheet health (6 items)
Search: "{Company} {TICKER} balance sheet debt cash current ratio 2025 2026"
- Total Debt, Net Debt/EBITDA, Interest Coverage, Current Ratio, Cash & Equivalents, Debt/Equity

### 8. Profitability & margins (6 items)
Search: "{Company} {TICKER} gross margin operating margin net margin ROE ROIC"
- Gross Margin, Operating Margin, Net Margin, ROE, ROIC, Asset Turnover

### 9. Cash flow (6 items)
Search: "{Company} {TICKER} operating cash flow free cash flow capex dividends buybacks"
- Op. Cash Flow (TTM), Free Cash Flow (TTM), Capex (TTM), FCF Margin, Div. Yield / Payout Ratio, Buybacks (TTM)

### 10. Growth profile (6 items)
Search: "{Company} {TICKER} revenue EPS growth CAGR estimates consensus 2026 2027"
- Rev CAGR (3Y), EPS CAGR (3Y), Next Q Est. Revenue, Next Q Est. EPS, FY Est. Revenue (current), FY Est. Revenue (next)

### 11. Ownership, sentiment, risks & catalysts (required)

This section should be substantive — not a brief closing paragraph. Gather the tables **and** detailed prose below.

**Ownership & analyst tables**

Search: `"{Company} {TICKER} institutional ownership insider buying short interest"`
- Institutional Ownership %, Insider Ownership %, Recent Insider Activity, Short Interest %

Search: `"{Company} {TICKER} analyst price target rating consensus"`
- Consensus Rating, Mean Price Target, # Buy/Hold/Sell, vs Current Price

**Sentiment analysis** (`sentiment_analysis`, 3-5 sentences)

Interpret what ownership and market data imply: institutional accumulation/distribution, insider buying vs selling patterns, short interest level and trend, analyst rating skew, and whether price trades above/below consensus. Cite sources inline.

**Key risks** (`key_risks`, 5-8 sentences)

Cover multiple categories where relevant:
- Operational / execution (seasonality, supply chain, customer concentration)
- Competitive / market share
- Financial / valuation (premium multiple, margin pressure)
- Regulatory / legal / geopolitical
- Macro / commodity / FX

Be specific to the company — not generic boilerplate. Cite filings or news where possible.

**Catalysts** (`catalysts`, 5-8 sentences)

Near- to medium-term events that could move the stock:
- Next earnings date (estimate if not confirmed)
- Guidance updates, product launches, M&A, regulatory decisions
- Contract wins/losses, capacity expansions, index inclusion
- Include timing (month/quarter) when available

Search: `"{Company} {TICKER} risks catalysts upcoming events earnings date 2026"`

### 14. References & citations (required)

Every report must include source attribution for key figures.

**Build a numbered reference list** (`references` in JSON) covering all sources used — typically 6-12 entries:
- SEC filings (10-K, 10-Q, 8-K)
- Earnings press releases / investor relations pages
- Market data providers (Yahoo Finance, etc.)
- Industry/market-share reports (Circana, Statista, company citations)
- Official product pages (for product URLs)

**Inline citations:** Append bracketed reference numbers to key numeric claims in tables and prose, e.g.:
- `"$496.3M [3]"` in segment metrics
- `">40% [2]"` for market share
- `"61.1x [5]"` in valuation
- `"FY2025 net sales of $610M [1]"` in outlook text

Cite at minimum: segment revenues, market shares, annual/quarterly revenue & EPS, valuation multiples, consensus targets, and competitor scale/share figures. Prose-only sections still cite major factual claims.

**Product URLs:** For each consumer-facing line in `segment_details`, add a `url` field linking to:
1. The official product/brand page on the company website, or
2. A direct purchase page (Amazon brand store, company shop) if no intro page exists

Geographic or B2B-only segments may omit `url` or link to the relevant investor/segment overview page.

## Output — PDF generation

After gathering all data, write a JSON file to `/tmp/{TICKER}_data.json` with the following structure, then run the PDF generator script.

### JSON schema

```json
{
  "company_name": "Full Company Name",
  "ticker": "TICK",
  "sector": "Sector / Industry",
  "date": "YYYY-MM-DD",
  "business_overview": "2-3 sentence high-level overview (no product deep-dive here)...",
  "segment_overview": "1-2 sentences on how the company reports segments and what drives the revenue mix.",
  "segment_summary": [
    ["Segment / Product Line", "Revenue", "YoY Growth", "Margin", "% Mix"],
    ["Google Search & Ads", "$198.0B", "+12.3%", "38.5%", "57.2%"],
    ["YouTube Ads", "$36.1B", "+14.8%", "N/A", "10.4%"],
    ["Google Cloud", "$43.2B", "+28.4%", "17.2%", "12.5%"]
  ],
  "segment_details": [
    {
      "name": "Google Search & Ads",
      "url": "https://ads.google.com/",
      "products": "Search ads, Performance Max, Google Network, Maps ads",
      "metrics": [
        ["Revenue (FY25)", "$198.0B [1]"],
        ["YoY Growth", "+12.3% [1]"],
        ["Operating Margin", "38.5% [1]"],
        ["% of Total", "57.2% [1]"]
      ],
      "outlook": "2-4 sentences with inline citations, e.g. share gains in AI Overviews [2]."
    }
  ],
  "industry_overview": "2-3 sentences on market size, growth, structure, and key industry trends.",
  "competitor_summary": [
    ["Company", "Scale", "Market Share", "Key Strength", "vs Subject"],
    ["Alphabet (GOOGL)", "$350B rev", "90% search", "Distribution + AI", "Benchmark"],
    ["Meta (META)", "$165B rev", "N/A", "Social graph", "Competes in ads, weaker search"],
    ["Amazon (AMZN)", "$650B rev", "N/A", "Commerce intent", "Retail media rival"]
  ],
  "competitive_assessment": "2-4 sentences summarizing competitive position, share trends, and strategic threats/opportunities.",
  "value_chain_overview": "1-2 sentences describing where the company sits in the value chain.",
  "major_customers": [
    ["Customer / Channel", "Key Companies", "% Rev / Notes"],
    ["Mass retail", "Walmart, Target, Kroger", "~45% via retail channel"],
    ["Club stores", "Costco, Sam's Club", "Growing; not individually disclosed"]
  ],
  "upstream_partners": [
    ["Input / Supplier", "Key Companies", "Role / Notes"],
    ["Contract manufacturing", "Foxconn, Pegatron", "Assembly; multi-source"],
    ["Raw materials", "TSMC (indirect)", "Chip supply dependency"]
  ],
  "downstream_channels": [
    ["Channel", "Key Companies", "Role / Notes"],
    ["Direct-to-consumer", "Company website, app", "~15% of sales"],
    ["Enterprise resellers", "Ingram Micro, CDW", "B2B distribution"]
  ],
  "value_chain_assessment": "2-4 sentences on customer concentration, supplier dependency, and channel mix risks.",
  "valuation": [
    ["P/E (TTM)", "25.3x"],
    ["Fwd P/E", "21.1x"],
    ["P/S (TTM)", "5.2x"],
    ["EV/EBITDA", "18.4x"],
    ["PEG Ratio", "1.5x"],
    ["FCF Yield", "3.2%"]
  ],
  "annual_financials": [
    ["FY2025", "$21.2B", "$1.45", "+18.2%", "+26.6%"],
    ["FY2024", "$17.9B", "$1.15", "+12.1%", "+15.3%"],
    ["FY2023", "$16.0B", "$1.00", "+8.4%", "+10.2%"],
    ["FY2022", "$14.7B", "$0.91", "+5.6%", "-2.1%"],
    ["FY2021", "$13.9B", "$0.93", "N/A", "N/A"]
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
  "sentiment_analysis": "3-5 sentences interpreting institutional ownership, insider activity, short interest, and analyst skew vs current price [N].",
  "key_risks": "5-8 sentences across operational, competitive, financial/valuation, regulatory, and macro risks [N].",
  "catalysts": "5-8 sentences on dated near-term events: earnings, guidance, product launches, regulatory milestones [N].",
  "references": [
    [1, "Alphabet Inc. Form 10-K (FY2025)", "https://www.sec.gov/..."],
    [2, "Alphabet Q1 FY2026 Earnings Release", "https://abc.xyz/investor/..."],
    [3, "Yahoo Finance - GOOGL", "https://finance.yahoo.com/quote/GOOGL"]
  ]
}
```

### Formatting rules for JSON values

- Revenue: use appropriate unit — "$X.XB" for billions, "$X.XM" for millions
- EPS: two decimal places with dollar sign, e.g. "$1.45" or "-$0.21"
- Ratios: one decimal with "x" suffix, e.g. "18.4x"
- Percentages: one decimal with "%" suffix, e.g. "+12.3%" or "-5.1%"
- Prefix positive growth with "+", negative with "-"
- If a value is unavailable after searching, use "N/A"
- `annual_financials`: exactly 5 rows (last 5 fiscal years); columns are Year, Revenue, EPS, YoY Rev %, YoY EPS %
- `quarterly_financials`: exactly 6 rows; columns are Quarter, Revenue, EPS, YoY Rev %
- For the oldest annual year, use "N/A" for YoY columns if no prior-year base exists
- `segment_summary`: include header row; add one row per material segment (3-8 rows typical)
- `segment_details`: one object per row in `segment_summary` (excluding header); `outlook` is required prose, not bullet points
- `competitor_summary`: include header row; first data row is the subject company; add 4-7 competitor rows
- `major_customers`, `upstream_partners`, `downstream_channels`: include header row; 3-6 data rows each
- Use channel types instead of inventing customer names when filings do not disclose them
- **Citations:** append ` [N]` immediately after cited values in strings (no comma before bracket); number `N` must exist in `references`
- `references`: array of `[id, "Source title", "https://..."]`; ids are integers starting at 1; URLs required (use landing page if exact page unavailable)
- `segment_details[].url`: optional HTTPS link shown under the product-line heading; required for consumer product lines when an official page exists
- `sentiment_analysis`, `key_risks`, `catalysts`: all three required; each must be multi-sentence prose with inline citations

### Generate the PDF

```bash
source ~/stock-study/.venv/bin/activate && python3 /Users/yihao/dev/agent-skills/stock-study/generate_pdf.py /tmp/{TICKER}_data.json
```

The script outputs the PDF path. Send the PDF file to the user with SendUserFile after generation.

## Final checks

- Did you cross-check financials against 2+ sources?
- Are all 14 sections populated (or marked N/A where data is truly unavailable)?
- Are `sentiment_analysis`, `key_risks`, and `catalysts` each substantive (not 1-2 sentences)?
- Does every key financial figure have an inline `[N]` citation pointing to a valid `references` entry?
- Are `references` complete with working URLs, rendered at the end of the PDF?
- Do consumer `segment_details` entries include `url` links to official product or purchase pages?
- Does `competitor_summary` include the subject company and 4+ peers with a relative comparison column?
- Do `major_customers`, `upstream_partners`, and `downstream_channels` name real companies or clearly labeled channel types?
- Do `annual_financials` (5 years) and `quarterly_financials` (6 quarters) both include YoY revenue growth?
- Does `segment_details` cover every material product line / reported segment, each with its own outlook?
- Do segment revenues reconcile roughly to consolidated revenue?
- Is the JSON valid before running the script?
- Did the PDF generate successfully and get sent to the user?
