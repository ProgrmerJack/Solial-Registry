#!/usr/bin/env python3
"""Export exact audit cases as analysis-ready CSV tables; no new estimation."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from social_registry.provenance import validated_audit


def flatten(row, prefix=""):
    result = {}
    for key, value in row.items():
        name = prefix + key
        if isinstance(value, dict):
            result.update(flatten(value, name + "."))
        else:
            result[name] = value
    return result


def export():
    audit = validated_audit(ROOT / "results/audit/legal_rule_audit.json")
    extension = audit["extended_analysis"]
    tables = {"income_boundaries": audit["income_boundary_cases"],
              "land_original_cases": audit["land_cases"],
              "self_employment": audit["self_employment_coefficient_comparison"]}
    for name, rows in extension.items():
        if isinstance(rows, list):
            tables[name] = rows
    folder = ROOT / "results/tables"
    folder.mkdir(exist_ok=True)
    counts = {}
    for name, rows in tables.items():
        rows = [flatten(row) for row in rows]
        fields = list(dict.fromkeys(key for row in rows for key in row))
        with (folder / f"{name}.csv").open("w", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        # Actual round-trip check: strings, booleans and blanks intentionally exported as text.
        with (folder / f"{name}.csv").open(newline="") as saved:
            loaded = list(csv.DictReader(saved))
        if len(loaded) != len(rows):
            raise ValueError(f"Export row count changed: {name}")
        for source, stored in zip(rows, loaded):
            for field in fields:
                expected = "" if source.get(field) is None else str(source.get(field, ""))
                if stored[field] != expected:
                    raise ValueError(f"Export value changed: {name}:{field}")
        counts[name] = len(rows)
    print(json.dumps({"csv_rows": counts, "validation": "all exported cells and row counts round-trip exactly"}, indent=2))


if __name__ == "__main__":
    export()
