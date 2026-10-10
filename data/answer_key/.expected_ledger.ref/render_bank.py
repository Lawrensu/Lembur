"""Render the synthetic bank CSV exclusively from manifest bank_lines."""

import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path


MANIFEST = Path(__file__).resolve().with_name("render_manifest.json")
OUTPUT = (
    Path(__file__).resolve().parents[3]
    / "data/demo/inbox/bank_statement_2026-W41_SYNTHETIC.csv"
)
FIELDS = ("date", "description", "type", "amount_rm", "bank_reference")


def main():
    with MANIFEST.open(encoding="utf-8") as source:
        bank_lines = json.load(source, parse_float=Decimal, parse_int=Decimal)[
            "bank_lines"
        ]

    references = [line["bank_reference"] for line in bank_lines]
    if len(bank_lines) != 14 or len(set(references)) != 14:
        raise ValueError("Expected 14 bank lines with unique references")
    if not all(reference.startswith("DEMO-") for reference in references):
        raise ValueError("Every synthetic bank reference must start with DEMO-")

    rows = []
    for line in bank_lines:
        if set(line) != set(FIELDS):
            raise ValueError("Bank line fields must match the CSV headers")
        if date.fromisoformat(line["date"]).isoformat() != line["date"]:
            raise ValueError("Bank dates must use ISO YYYY-MM-DD format")
        amount = line["amount_rm"]
        if not amount.is_finite() or Decimal(format(amount, ".2f")) != amount:
            raise ValueError("Bank amounts must be finite and exact to two decimals")
        rows.append({**line, "amount_rm": format(amount, ".2f")})

    with OUTPUT.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    with OUTPUT.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != list(FIELDS):
            raise ValueError("CSV headers differ from the required headers")
        parsed = list(reader)
    if parsed != rows:
        raise ValueError("CSV text did not round-trip exactly")
    for row in parsed:
        row["amount_rm"] = Decimal(row["amount_rm"])
    if parsed != bank_lines:
        raise ValueError("Parsed CSV differs from manifest bank_lines")

    print(f"Wrote {OUTPUT}")
    print("Verified: 14 rows equal bank_lines in order; 14 unique DEMO references.")


if __name__ == "__main__":
    main()
