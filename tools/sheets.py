"""Read and write the CSV data files as plain strings.

A book is a dict of sheet name to a list of rows; a row is a dict of column
name to string, with "" for an empty cell. Every sheet is one CSV file named
<base>_<sheet>.csv (docs/SYSTEM_DESIGN.md 3.1).
"""

from __future__ import annotations

import csv
import os
from decimal import InvalidOperation

from conventions import is_empty, rm, text, to_sen
from schema import MONEY_COLUMNS


def _check_format(fmt) -> None:
    if fmt != "csv":
        raise ValueError("Unknown format %r; only 'csv' is supported." % (fmt,))


def _csv_path(path, sheet):
    return "%s_%s.csv" % (os.path.splitext(str(path))[0], sheet)


def _shape(raw_rows, columns):
    """Keep the wanted columns in order and drop rows that are entirely empty."""
    rows = []
    for raw in raw_rows:
        row = {name: text(raw.get(name)) for name in columns}
        if any(row.values()):
            rows.append(row)
    return rows


def _read_csv_sheet(path, columns):
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        raw_rows = [
            {text(key): value for key, value in record.items() if key is not None}
            for record in reader
        ]
    return _shape(raw_rows, columns)


def load_book(path, sheet_columns, fmt="csv") -> dict:
    """Read every sheet in sheet_columns into a book of string rows.

    Missing files give an empty list. Extra columns are ignored and missing
    ones come back as "".
    """
    _check_format(fmt)
    return {
        sheet: _read_csv_sheet(_csv_path(path, sheet), columns)
        for sheet, columns in sheet_columns.items()
    }


def _csv_value(column, value):
    if column in MONEY_COLUMNS and not is_empty(value):
        try:
            return rm(to_sen(value))
        except InvalidOperation:
            pass
    return text(value)


def save_book(path, sheet_columns, book, fmt="csv") -> None:
    """Write every sheet in sheet_columns from the book."""
    _check_format(fmt)
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    for sheet, columns in sheet_columns.items():
        with open(_csv_path(path, sheet), "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(columns)
            for row in book.get(sheet, []):
                writer.writerow([_csv_value(name, row.get(name)) for name in columns])
