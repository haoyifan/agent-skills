---
name: str-bank-statement-bookkeeping
description: Record monthly short-term-rental LLC bank statement transactions into a bookkeeping workbook stored in Google Drive. Use when the user sends a monthly LLC bank statement PDF and wants property income/expenses entered into an existing workbook tab (for example, yearly tabs like 2025/2026) while ignoring owner payouts/distributions and preserving separate property-specific columns versus general LLC columns.
---

# STR Bank Statement Bookkeeping

Use this skill to update a recurring LLC bookkeeping workbook from a monthly bank statement.

## Core workflow

1. Read the monthly bank statement PDF.
2. Extract all transactions for the statement period.
3. Apply the user's classification rules for that LLC/workbook.
4. Decide which transactions should be recorded and which should be ignored.
5. Open the target workbook and locate the correct **year tab**.
6. Append new rows without disturbing prior rows or formulas.
7. Review totals with the user after updating.

## Default bookkeeping model

Treat the workbook as a **cash ledger first**, not a final tax-treatment ledger.

Record transactions faithfully into the workbook according to the user's bookkeeping rules. Do not silently convert entries into tax categories unless the user explicitly asks.

## Stillwater LLC rules

For the current Stillwater workflow:

- Workbook: **[Stillwater] LLC transaction records.xlsx**
- Property-specific columns for **6880 Moss Ln** are only for that property's income and expenses.
- **General** columns are only for LLC-wide costs/income not tied to one specific property.
- Use the tab matching the transaction year, for example:
  - 2025 transactions → **2025** tab
  - 2026 transactions → **2026** tab

### Bank statement recording rules

When the user provides the monthly LLC bank statement:

- **Record income** from channels such as Airbnb, VRBO, Booking.com into the property's **income** column.
- **Record mortgage payments** into the property's **cost** column when the user says mortgage should be tracked in the ledger.
- **Do not record owner payouts/distributions** such as ACH transfers to the owner when the user says to ignore them.
- Handle out-of-pocket reimbursement/expense files separately; do not mix them into the bank-statement pass unless explicitly requested.

## Required checks before editing

Before writing to the workbook:

- Confirm the target workbook file.
- Confirm the correct year tab.
- Confirm the specific property section/columns to use.
- Identify any transactions that should be excluded under the user's rule set.

## Row placement convention

Append new rows at the end of the active year's ledger unless the workbook clearly uses another insertion convention.

For Stillwater's current layout:

- Column A: date
- Column B: 6880 Moss Ln cost
- Column C: 6880 Moss Ln income
- Column D: description/summary
- Column E: general LLC cost
- Column F: general LLC income

If the workbook layout changes, inspect it first instead of assuming the same column positions.

## Output to the user after each update

After updating, summarize:

- which transactions were recorded
- which transactions were ignored
- total income recorded for the month
- total cost recorded for the month
- any uncertain/classification-sensitive items

## Safety rules

- Do not overwrite the workbook blindly; preserve existing data.
- Do not record owner transfers/distributions when the user says to exclude them.
- Do not treat a raw bank statement as the final tax ledger.
- If a transaction is ambiguous between property-specific and general LLC, ask or flag it.
- Prefer updating the user's Google Drive master workbook once write access is confirmed.

## Drive update workflow

If Google Drive write access is available:

1. Locate the target workbook in Drive.
2. Download or use a safe editable local copy.
3. Update the correct tab.
4. Upload/update the Drive master file.
5. Tell the user exactly what changed.

If Drive write access is not available, prepare exact rows for user review first.
