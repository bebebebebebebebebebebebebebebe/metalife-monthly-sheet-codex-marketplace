#!/usr/bin/env python3
"""Parse a MetaLife timecard CSV into daily monthly-sheet rows.

The output is JSON intended for Codex/Google Sheets update workflows. It does
not write to Google Sheets.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = [
    "種別",
    "日時",
    "曜日",
    "編集履歴",
    "場所",
    "勤務時間(分)",
    "累計勤務時間(分)",
]

ENCODINGS = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]


def read_csv(path: Path) -> tuple[str, list[dict[str, str]], list[str]]:
    errors: list[str] = []
    for encoding in ENCODINGS:
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                rows = list(csv.DictReader(handle))
            columns = list(rows[0].keys()) if rows else []
            if all(col in columns for col in REQUIRED_COLUMNS):
                return encoding, rows, columns
            errors.append(f"{encoding}: missing required columns; got {columns}")
        except UnicodeDecodeError as exc:
            errors.append(f"{encoding}: decode error: {exc}")
        except csv.Error as exc:
            errors.append(f"{encoding}: csv error: {exc}")
    raise SystemExit(
        json.dumps(
            {
                "error": "Could not read MetaLife CSV with required columns.",
                "required_columns": REQUIRED_COLUMNS,
                "attempts": errors,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def int_or_none(value: str) -> int | None:
    value = (value or "").strip()
    if value.isdigit():
        return int(value)
    return None


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")


def round_hours(minutes: int) -> float:
    return round(minutes / 60, 2)


def build_output(path: Path) -> dict[str, Any]:
    encoding, rows, columns = read_csv(path)
    row_minutes_by_date: dict[str, int] = defaultdict(int)
    cumulative_delta_by_date: dict[str, int] = defaultdict(int)
    statuses_by_date: dict[str, set[str]] = defaultdict(set)
    locations_by_date: dict[str, set[str]] = defaultdict(set)
    edited_dates: set[str] = set()
    warnings: list[str] = []

    previous_cumulative = 0
    last_cumulative: int | None = None

    for index, row in enumerate(rows, start=2):
        raw_dt = row.get("日時", "").strip()
        if not raw_dt:
            warnings.append(f"row {index}: missing 日時")
            continue
        try:
            dt = parse_dt(raw_dt)
        except ValueError:
            warnings.append(f"row {index}: invalid 日時 {raw_dt!r}")
            continue

        date = dt.strftime("%Y/%m/%d")
        kind = row.get("種別", "").strip()
        location = row.get("場所", "").strip()
        edit_history = row.get("編集履歴", "").strip()

        if kind:
            statuses_by_date[date].add(kind)
        if location and location != "-":
            locations_by_date[date].add(location)
        if edit_history and edit_history != "-":
            edited_dates.add(date)

        row_minutes = int_or_none(row.get("勤務時間(分)", ""))
        if row_minutes is not None:
            row_minutes_by_date[date] += row_minutes

        cumulative = int_or_none(row.get("累計勤務時間(分)", ""))
        if cumulative is not None:
            delta = cumulative - previous_cumulative
            if delta < 0:
                warnings.append(
                    f"row {index}: cumulative minutes decreased from "
                    f"{previous_cumulative} to {cumulative}"
                )
            cumulative_delta_by_date[date] += delta
            previous_cumulative = cumulative
            last_cumulative = cumulative

    all_dates = sorted(set(row_minutes_by_date) | set(cumulative_delta_by_date))
    daily_rows: list[dict[str, Any]] = []
    for date in all_dates:
        row_minutes = row_minutes_by_date.get(date, 0)
        cumulative_delta = cumulative_delta_by_date.get(date, 0)
        locations = sorted(locations_by_date.get(date, set()))
        daily_rows.append(
            {
                "date": date,
                "locations": locations,
                "suggested_status": "リモート" if "リモート" in locations else "出勤",
                "minutes_from_work_rows": row_minutes,
                "hours_from_work_rows": round_hours(row_minutes),
                "minutes_from_cumulative_delta": cumulative_delta,
                "hours_from_cumulative_delta": round_hours(cumulative_delta),
                "source_event_types": sorted(statuses_by_date.get(date, set())),
                "has_edit_history": date in edited_dates,
                "late_or_early": False,
            }
        )

    total_row_minutes = sum(row_minutes_by_date.values())
    total_cumulative_delta = sum(cumulative_delta_by_date.values())
    requires_confirmation = total_row_minutes != total_cumulative_delta
    if requires_confirmation:
        warnings.append(
            "勤務時間(分)合計 and 累計勤務時間(分)差分 differ; user must choose basis."
        )

    return {
        "source_file": str(path),
        "encoding": encoding,
        "columns": columns,
        "row_count": len(rows),
        "daily_row_count": len(daily_rows),
        "daily_rows": daily_rows,
        "totals": {
            "minutes_from_work_rows": total_row_minutes,
            "hours_from_work_rows": round_hours(total_row_minutes),
            "minutes_from_cumulative_delta": total_cumulative_delta,
            "hours_from_cumulative_delta": round_hours(total_cumulative_delta),
            "last_cumulative_minutes": last_cumulative,
            "last_cumulative_hours": round_hours(last_cumulative)
            if last_cumulative is not None
            else None,
        },
        "warnings": warnings,
        "requires_confirmation": requires_confirmation,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()

    if not args.csv_path.exists():
        raise SystemExit(f"CSV file not found: {args.csv_path}")

    print(json.dumps(build_output(args.csv_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
