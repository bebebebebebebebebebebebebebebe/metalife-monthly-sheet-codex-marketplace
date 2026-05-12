---
name: metalife-monthly-sheet
description: Use when importing MetaLife timecard CSV exports into an existing monthly Google Sheets report while preserving headers, formulas, formatting, and summary cells.
---

# MetaLife Monthly Sheet

Use this skill when the user wants to turn a MetaLife勤怠CSV into rows in an existing Google Sheets monthly report.

The default path is Google Sheets API updates, not Chrome browser entry. Browser automation is only a fallback for inspection or user-visible confirmation.

## Required Inputs

- MetaLife CSV file path.
- Target Google Sheets URL or spreadsheet ID.
- Target sheet tab name, unless it can be confidently inferred from the workbook.
- Desired status mapping, if not obvious from the sheet. Default for rows whose work location is `リモート`: use `リモート`.

If any required input is missing and cannot be inferred from the environment or open spreadsheet context, ask for it before planning a write.

## Workflow

1. Read `scripts/parse_metalife_csv.py` only if you need implementation details; otherwise run it directly.
2. Parse the CSV with the script and inspect the JSON summary.
3. Read `references/sheets-update.md` before any Google Sheets write.
4. Read spreadsheet metadata, target sheet headers, input table cells, and nearby summary cells.
5. Detect the monthly input table by headers, not by a fixed range:
   - `日付`
   - `勤怠ステータス`
   - `勤務時間 (h)`
   - `遅刻/早退`
6. Compare time calculation modes:
   - row `勤務時間(分)` sum
   - `累計勤務時間(分)` deltas
   - optional timestamp-pair calculation when needed
7. Stop and ask the user before writing if:
   - required CSV columns are missing,
   - the target sheet/table cannot be identified,
   - the time calculation modes materially disagree,
   - writing would affect formulas, headers, or summary cells,
   - a status mapping is ambiguous.
8. If safe, update only table values. Preserve formats, formulas, validations, dimensions, and summary cells.
9. Re-read the written range and summary range. Report row count, total hours, summary values, cleared range, and the sheet link.

## CSV Parsing

Run:

```bash
python scripts/parse_metalife_csv.py "path/to/timecard.csv"
```

The script emits JSON with:

- `encoding`
- `columns`
- `daily_rows`
- `totals`
- `warnings`
- `requires_confirmation`

Use `daily_rows[].hours_from_cumulative_delta` as the preferred value only after confirming that cumulative deltas are the intended basis or that no meaningful discrepancy exists. If discrepancies exist, present the options and ask the user which basis to use.

## Sheets Update Rules

- Use Google Sheets MCP/API tools for existing spreadsheets.
- Use `get_spreadsheet_metadata` before reading or writing ranges.
- Use `get_spreadsheet_cells` before writing values into an existing table so formulas, formats, validation, and typed values are visible.
- Write dates as typed date-compatible values that preserve the existing date number format.
- Write hours as numbers, not strings.
- Write late/early flags as booleans, not strings, when the sheet counts `TRUE`.
- Clear only old input values below the new data rows inside the detected input table.
- Never clear or rewrite headers, formula cells, or summary tables.

## Reporting

Final responses after a successful update must include:

- Target spreadsheet and sheet tab.
- Number of rows written.
- Total hours used for the update.
- Summary cell values checked, especially remote/work status count, late/early count, and total hours.
- Cleared empty input range.
- Google Sheets link.

If the write was skipped, report the blocking reason and the exact user decision needed.
