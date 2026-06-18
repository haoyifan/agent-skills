#!/usr/bin/env python3
"""Generate a nicely formatted fundamental stock research PDF report."""

import json
import sys
import os


from fpdf import FPDF

UNICODE_REPLACEMENTS = {
    "—": "-",   # em dash
    "–": "-",   # en dash
    "‘": "'",   # left single quote
    "’": "'",   # right single quote
    "“": '"',   # left double quote
    "”": '"',   # right double quote
    "…": "...", # ellipsis
    "•": "*",   # bullet
    " ": " ",   # non-breaking space
}


def sanitize(text):
    for char, replacement in UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    return text


class StockReport(FPDF):
    DARK_BLUE = (26, 54, 93)
    MEDIUM_BLUE = (44, 82, 130)
    LIGHT_BLUE = (219, 234, 254)
    LIGHT_GRAY = (243, 244, 246)
    WHITE = (255, 255, 255)
    BLACK = (30, 30, 30)
    DARK_GRAY = (107, 114, 128)
    GREEN = (22, 101, 52)
    RED = (185, 28, 28)

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*self.DARK_GRAY)
            header_text = sanitize(f"{self.data['company_name']} ({self.data['ticker']})")
            self.cell(95, 6, header_text, align="L")
            self.cell(95, 6, self.data.get("date", ""), align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(200, 200, 200)
            self.set_line_width(0.3)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*self.DARK_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def _color_for_value(self, cell):
        if not isinstance(cell, str):
            return self.BLACK
        stripped = cell.strip()
        if stripped.startswith("-") and any(c.isdigit() for c in stripped):
            return self.RED
        if stripped.startswith("+") and any(c.isdigit() for c in stripped):
            return self.GREEN
        return self.BLACK

    def add_title_block(self):
        self.set_fill_color(*self.DARK_BLUE)
        self.rect(0, 0, 210, 48, "F")

        self.set_fill_color(*self.MEDIUM_BLUE)
        self.rect(0, 48, 210, 4, "F")

        self.set_y(10)
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*self.WHITE)
        self.cell(0, 12, sanitize(self.data["company_name"]), align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 14)
        ticker_sector = f"({self.data['ticker']})"
        if self.data.get("sector"):
            ticker_sector += f"  |  {self.data['sector']}"
        self.cell(0, 8, sanitize(ticker_sector), align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "I", 10)
        self.set_text_color(180, 200, 230)
        self.cell(0, 8, sanitize(f"Fundamental Research Report  |  {self.data.get('date', '')}"), align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_y(56)

    def add_section_header(self, title, new_page=False):
        if new_page:
            self.add_page()
        elif self.get_y() > 265:
            self.add_page()
        self.set_fill_color(*self.MEDIUM_BLUE)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.WHITE)
        self.cell(190, 7, sanitize(f"  {title}"), fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def add_paragraph(self, text):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*self.BLACK)
        self.multi_cell(190, 5, sanitize(text))
        self.ln(1)

    def add_subsection_header(self, title):
        if self.get_y() > 265:
            self.add_page()
        self.set_fill_color(*self.LIGHT_BLUE)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*self.DARK_BLUE)
        self.cell(190, 6, sanitize(f"  {title}"), fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def add_subsection_header_with_url(self, title, url=None):
        self.add_subsection_header(title)
        if url:
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(*self.MEDIUM_BLUE)
            self.cell(190, 4, sanitize(f"  {url}"), link=url, new_x="LMARGIN", new_y="NEXT")
            self.ln(1)
            self.set_text_color(*self.BLACK)

    def add_labeled_text(self, label, text):
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*self.DARK_BLUE)
        self.cell(0, 5, sanitize(f"{label} "), new_x="LMARGIN", new_y="NEXT")
        self.add_paragraph(text)

    def add_segment_detail(self, segment):
        if self.get_y() > 250:
            self.add_page()

        self.add_subsection_header_with_url(segment.get("name", "Segment"), segment.get("url"))

        if segment.get("products"):
            self.add_labeled_text("Products:", segment["products"])

        if segment.get("metrics"):
            self.add_kv_table(segment["metrics"], cols=2)

        if segment.get("outlook"):
            self.add_labeled_text("Outlook:", segment["outlook"])

        self.ln(1)

    def add_table(self, headers, rows, col_widths=None, first_col_align="L"):
        if not col_widths:
            col_widths = [190 / len(headers)] * len(headers)

        self.set_fill_color(*self.DARK_BLUE)
        self.set_text_color(*self.WHITE)
        self.set_font("Helvetica", "B", 8.5)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)

        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, sanitize(f" {h}"), border=1, fill=True, align="C")
        self.ln()

        self.set_font("Helvetica", "", 8.5)
        for row_idx, row in enumerate(rows):
            if row_idx % 2 == 0:
                self.set_fill_color(*self.WHITE)
            else:
                self.set_fill_color(*self.LIGHT_GRAY)

            for i, cell in enumerate(row):
                color = self._color_for_value(cell)
                self.set_text_color(*color)
                align = first_col_align if i == 0 else "R"
                self.cell(col_widths[i], 6.5, sanitize(f" {cell} "), border=1, fill=True, align=align)
            self.ln()

        self.set_text_color(*self.BLACK)
        self.ln(1)

    def add_kv_table(self, items, cols=2):
        pair_w = 190 / cols
        key_w = pair_w * 0.58
        val_w = pair_w * 0.42

        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)

        for i in range(0, len(items), cols):
            chunk = items[i : i + cols]
            if (i // cols) % 2 == 0:
                self.set_fill_color(*self.WHITE)
            else:
                self.set_fill_color(*self.LIGHT_GRAY)

            for key, val in chunk:
                self.set_font("Helvetica", "B", 8.5)
                self.set_text_color(*self.DARK_BLUE)
                self.cell(key_w, 6.5, sanitize(f" {key}"), border=1, fill=True, align="L")

                self.set_font("Helvetica", "", 8.5)
                color = self._color_for_value(val)
                self.set_text_color(*color)
                self.cell(val_w, 6.5, sanitize(f"{val} "), border=1, fill=True, align="R")

            remaining = cols - len(chunk)
            for _ in range(remaining):
                self.cell(key_w, 6.5, "", border=1, fill=True)
                self.cell(val_w, 6.5, "", border=1, fill=True)
            self.ln()

        self.set_text_color(*self.BLACK)
        self.ln(1)

    def add_risk_sentiment_section(self):
        has_tables = self.data.get("ownership") or self.data.get("analyst_consensus")
        has_prose = (
            self.data.get("sentiment_analysis")
            or self.data.get("key_risks")
            or self.data.get("catalysts")
            or self.data.get("risks_catalysts")
        )
        if not has_tables and not has_prose:
            return

        self.add_section_header("Risk, Catalysts & Market Sentiment")

        if self.data.get("ownership") and self.data.get("analyst_consensus"):
            self.add_two_column_section(
                "Ownership & Sentiment",
                self.data["ownership"],
                "Analyst Consensus",
                self.data["analyst_consensus"],
            )
        else:
            if self.data.get("ownership"):
                self.add_subsection_header("Ownership & Sentiment")
                self.add_kv_table(self.data["ownership"], cols=2)
            if self.data.get("analyst_consensus"):
                self.add_subsection_header("Analyst Consensus")
                self.add_kv_table(self.data["analyst_consensus"], cols=2)

        if self.data.get("sentiment_analysis"):
            self.add_labeled_text("Sentiment Analysis:", self.data["sentiment_analysis"])
        if self.data.get("key_risks"):
            self.add_labeled_text("Key Risks:", self.data["key_risks"])
        if self.data.get("catalysts"):
            self.add_labeled_text("Catalysts:", self.data["catalysts"])
        elif self.data.get("risks_catalysts") and not (
            self.data.get("key_risks") or self.data.get("catalysts")
        ):
            self.add_labeled_text("Risks & Catalysts:", self.data["risks_catalysts"])

    def add_references(self):
        refs = self.data.get("references")
        if not refs:
            return

        self.add_page()
        self.add_section_header("References")
        for ref in refs:
            if self.get_y() > 270:
                self.add_page()

            ref_id = ref[0]
            title = ref[1] if len(ref) > 1 else ""
            url = ref[2] if len(ref) > 2 else ""

            self.set_font("Helvetica", "B", 8.5)
            self.set_text_color(*self.DARK_BLUE)
            self.cell(10, 5, sanitize(f"[{ref_id}]"), new_x="END")

            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(*self.BLACK)
            self.cell(0, 5, sanitize(f" {title}"), new_x="LMARGIN", new_y="NEXT")

            if url:
                self.set_font("Helvetica", "", 7.5)
                self.set_text_color(*self.MEDIUM_BLUE)
                self.set_x(20)
                self.cell(180, 4, sanitize(url), link=url, new_x="LMARGIN", new_y="NEXT")
                self.ln(1)
                self.set_text_color(*self.BLACK)

        self.ln(1)

    def add_two_column_section(self, left_title, left_items, right_title, right_items, new_page=False):
        if new_page:
            self.add_page()
        elif self.get_y() > 245:
            self.add_page()

        y_start = self.get_y()
        x_left = 10
        x_right = 105

        col_w = 90
        kw = col_w * 0.58
        vw = col_w * 0.42

        for side, (title, items, x_pos) in enumerate(
            [(left_title, left_items, x_left), (right_title, right_items, x_right)]
        ):
            self.set_xy(x_pos, y_start)
            self.set_fill_color(*self.MEDIUM_BLUE)
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*self.WHITE)
            self.cell(col_w, 7, sanitize(f"  {title}"), fill=True, new_x="LMARGIN", new_y="NEXT")

            row_y = y_start + 9
            self.set_draw_color(200, 200, 200)
            self.set_line_width(0.2)

            for idx, (key, val) in enumerate(items):
                self.set_xy(x_pos, row_y)
                if idx % 2 == 0:
                    self.set_fill_color(*self.WHITE)
                else:
                    self.set_fill_color(*self.LIGHT_GRAY)

                self.set_font("Helvetica", "B", 8.5)
                self.set_text_color(*self.DARK_BLUE)
                self.cell(kw, 6.5, sanitize(f" {key}"), border=1, fill=True, align="L")

                self.set_font("Helvetica", "", 8.5)
                color = self._color_for_value(val)
                self.set_text_color(*color)
                self.cell(vw, 6.5, sanitize(f"{val} "), border=1, fill=True, align="R")

                row_y += 6.5

        max_rows = max(len(left_items), len(right_items))
        self.set_y(y_start + 9 + max_rows * 6.5 + 2)
        self.set_text_color(*self.BLACK)

    def generate(self, output_path):
        self.alias_nb_pages()
        self.add_page()
        self.add_title_block()

        # Business Overview
        self.add_section_header("Business Overview")
        self.add_paragraph(self.data.get("business_overview", "N/A"))

        # Business Segments & Product Lines
        if self.data.get("segment_summary") or self.data.get("segment_details"):
            self.add_section_header("Business Segments & Product Lines")
            if self.data.get("segment_overview"):
                self.add_paragraph(self.data["segment_overview"])
            if self.data.get("segment_summary"):
                summary = self.data["segment_summary"]
                headers = summary[0]
                rows = summary[1:]
                if len(headers) == 5:
                    col_widths = [52, 34, 30, 30, 24]
                elif len(headers) == 4:
                    col_widths = [60, 44, 44, 42]
                else:
                    col_widths = None
                self.add_table(headers, rows, col_widths=col_widths)
            for segment in self.data.get("segment_details", []):
                self.add_segment_detail(segment)

        # Competitors & Industry Landscape
        if self.data.get("competitor_summary") or self.data.get("industry_overview"):
            self.add_section_header("Competitors & Industry Landscape")
            if self.data.get("industry_overview"):
                self.add_paragraph(self.data["industry_overview"])
            if self.data.get("competitor_summary"):
                summary = self.data["competitor_summary"]
                headers = summary[0]
                rows = summary[1:]
                if len(headers) == 5:
                    col_widths = [34, 30, 26, 48, 52]
                else:
                    col_widths = None
                self.add_table(headers, rows, col_widths=col_widths)
            if self.data.get("competitive_assessment"):
                self.add_labeled_text("Assessment:", self.data["competitive_assessment"])

        # Customers & Value Chain
        if (
            self.data.get("major_customers")
            or self.data.get("upstream_partners")
            or self.data.get("downstream_channels")
            or self.data.get("value_chain_overview")
        ):
            self.add_section_header("Customers & Value Chain")
            if self.data.get("value_chain_overview"):
                self.add_paragraph(self.data["value_chain_overview"])
            chain_tables = [
                ("Major Customers / Clients", "major_customers"),
                ("Upstream (Suppliers & Inputs)", "upstream_partners"),
                ("Downstream (Channels & Distribution)", "downstream_channels"),
            ]
            for title, key in chain_tables:
                if self.data.get(key):
                    self.add_subsection_header(title)
                    table = self.data[key]
                    headers = table[0]
                    rows = table[1:]
                    if len(headers) == 3:
                        col_widths = [42, 58, 90]
                    else:
                        col_widths = None
                    self.add_table(headers, rows, col_widths=col_widths)
            if self.data.get("value_chain_assessment"):
                self.add_labeled_text("Assessment:", self.data["value_chain_assessment"])

        # --- Page break: product / qualitative -> financial metrics ---
        has_financial = any(
            self.data.get(key)
            for key in (
                "valuation",
                "annual_financials",
                "quarterly_financials",
                "balance_sheet",
                "profitability",
                "cash_flow",
                "growth",
            )
        )
        if has_financial:
            self.add_page()

        # Valuation Metrics
        if self.data.get("valuation"):
            self.add_section_header("Valuation Metrics")
            self.add_kv_table(self.data["valuation"], cols=3)

        # Annual & Quarterly Financials
        if self.data.get("annual_financials") or self.data.get("quarterly_financials"):
            self.add_section_header("Financial Performance")
            if self.data.get("annual_financials"):
                self.add_subsection_header("Annual (Last 5 Fiscal Years)")
                headers = ["Fiscal Year", "Revenue", "EPS", "YoY Rev %", "YoY EPS %"]
                rows = self.data["annual_financials"]
                self.add_table(headers, rows, col_widths=[34, 40, 34, 38, 38])
            if self.data.get("quarterly_financials"):
                self.add_subsection_header("Quarterly (Last 6 Quarters)")
                headers = ["Quarter", "Revenue", "EPS", "YoY Rev %"]
                rows = self.data["quarterly_financials"]
                self.add_table(headers, rows, col_widths=[38, 52, 48, 52])

        # Balance Sheet + Profitability side-by-side
        if self.data.get("balance_sheet") and self.data.get("profitability"):
            self.add_two_column_section(
                "Balance Sheet",
                self.data["balance_sheet"],
                "Profitability & Margins",
                self.data["profitability"],
            )
        else:
            if self.data.get("balance_sheet"):
                self.add_section_header("Balance Sheet Health")
                self.add_kv_table(self.data["balance_sheet"], cols=3)
            if self.data.get("profitability"):
                self.add_section_header("Profitability & Margins")
                self.add_kv_table(self.data["profitability"], cols=3)

        # Cash Flow + Growth side-by-side
        if self.data.get("cash_flow") and self.data.get("growth"):
            self.add_two_column_section(
                "Cash Flow",
                self.data["cash_flow"],
                "Growth Profile",
                self.data["growth"],
            )
        else:
            if self.data.get("cash_flow"):
                self.add_section_header("Cash Flow")
                self.add_kv_table(self.data["cash_flow"], cols=2)
            if self.data.get("growth"):
                self.add_section_header("Growth Profile")
                self.add_kv_table(self.data["growth"], cols=2)

        # --- Page break: financial metrics -> risk / sentiment ---
        has_risk_sentiment = any(
            self.data.get(key)
            for key in (
                "ownership",
                "analyst_consensus",
                "sentiment_analysis",
                "key_risks",
                "catalysts",
                "risks_catalysts",
            )
        )
        if has_risk_sentiment:
            self.add_page()
            self.add_risk_sentiment_section()

        # References (adds its own page break)
        self.add_references()

        self.output(output_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_pdf.py <data.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    output_dir = os.path.expanduser("~/stock-study")
    os.makedirs(output_dir, exist_ok=True)

    ticker = data["ticker"]
    date_str = data.get("date", "report")
    output_path = os.path.join(output_dir, f"{ticker}_{date_str}.pdf")

    report = StockReport(data)
    report.generate(output_path)
    print(output_path)


if __name__ == "__main__":
    main()
