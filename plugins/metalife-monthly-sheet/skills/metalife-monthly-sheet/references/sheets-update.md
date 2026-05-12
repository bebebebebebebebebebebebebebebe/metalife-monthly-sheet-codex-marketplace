# Google Sheets Update Reference

Use this reference before applying MetaLife CSV data to an existing monthly Google Sheet.

## Target Discovery

1. Resolve the spreadsheet ID from the URL or user-provided ID.
2. Read metadata and list sheet tabs.
3. Choose the target tab by user instruction, current workbook context, or a month-like tab name. Ask if multiple plausible tabs exist.
4. Read a bounded area around the top-left of the likely report sheet.
5. Detect the input table header row by exact or near-exact headers:
   - `日付`
   - `勤怠ステータス`
   - `勤務時間 (h)`
   - `遅刻/早退`

Do not assume the table starts at `A1` unless the sheet read confirms it.

## Write Shape

Write only values into the detected input table columns:

| Column meaning | Value type | Notes |
| --- | --- | --- |
| Date | Date-compatible number or date value | Preserve the existing date format such as `yyyy/MM/dd`. |
| Attendance status | String | Use the chosen status mapping, commonly `リモート`. |
| Working hours | Number | Use decimal hours from the confirmed calculation basis. |
| Late/early | Boolean | Use `false` unless the source data explicitly indicates late/early. |

For Google Sheets API `updateCells`, set `fields` to `userEnteredValue` only. This preserves existing formats and validations.

## Clearing Old Rows

After writing the new rows, clear stale input values below the last new row and inside the detected table width.

Example:

- Header row: 1
- New data rows: 16
- Table columns: 4
- Existing input capacity: rows 2 through 35
- Write: rows 2 through 17
- Clear: rows 18 through 35

Only clear `userEnteredValue`. Do not clear `userEnteredFormat`, formulas, notes, validation, or dimensions.

## Summary Verification

After writing, read:

- The written input range.
- The cleared stale range.
- The nearby summary table or formulas that reference the monthly table.

Verify:

- row count equals parsed daily rows,
- stale rows are blank,
- status count matches the number of rows with that status,
- total hours is consistent with the written decimal hour values,
- late/early count is zero unless source data says otherwise.

If summary total differs from raw minute total by small rounding drift, explain whether the sheet sums rounded daily decimal hours or exact minutes.

## Stop Conditions

Do not write if:

- required headers are missing,
- the input table overlaps a summary/formula area,
- formulas exist in the target value cells,
- the sheet has data validation with incompatible allowed values,
- time calculation bases differ and the user has not chosen a basis,
- the user asked for browser-only entry and browser automation is unstable.
