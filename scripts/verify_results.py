#!/usr/bin/env python3
"""Independent algebra checks over existing audit cases, without engine imports."""
from fractions import Fraction
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(condition, message="Independent audit check failed"):
    if not condition:
        raise ValueError(message)


def coverage(rows, key, expected, label):
    """Check identity and multiplicity, not just a plausible number of rows."""
    check(Counter(key(row) for row in rows) == Counter(expected),
          f"Incomplete or duplicated {label} coverage")


def integer(value, *, allow_string=False):
    allowed = (str, int) if allow_string else (int,)
    check(type(value) in allowed, "Invalid integer case input type")
    exact = Fraction(value)
    check(exact.denominator == 1, "Noninteger case input")
    return exact.numerator


def boolean(value):
    check(type(value) is bool, "Invalid boolean case input type")
    return value


def verify(data=None, *, write_output=True):
    path = ROOT / "results/audit/legal_rule_audit.json"
    from_file = data is None
    if data is None:
        tested_bytes = path.read_bytes()
        data = json.loads(tested_bytes)
    elif write_output:
        raise ValueError("In-memory checks must not write a file attestation")
    else:
        tested_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    spec = data["rule_extraction_and_prespecified_inputs"]
    frozen = json.loads((ROOT / "data/rules/legal_specification.json").read_text())
    check(json.dumps(spec, sort_keys=True) == json.dumps(frozen, sort_keys=True),
          "Reported extraction differs from frozen inputs")
    p = Fraction(spec["minimum_consumption_monthly_per_person_soum"])
    m = Fraction(spec["minimum_remuneration_monthly_soum"])
    extension = data["extended_analysis"]
    plan = frozen["extension_prespecified_inputs"]
    coverage(extension["land_integer_grid"],
             lambda r: (integer(r["total_m2"], allow_string=True), integer(r["buildings_m2"], allow_string=True)),
             ((u, b) for u in plan["land_total_areas_m2"] for b in range(u+1)), "land")
    coverage(extension["hardship_boundary_cases"],
             lambda r: (r["boundary_multiple"], integer(r["offset_soum"])),
             ((a, d) for a in plan["hardship_boundary_multiples"] for d in plan["offsets_soum"]), "hardship")
    coverage(extension["tax_floor_cases"],
             lambda r: (r["region_class"], r["sex"], integer(r["offset_soum"])),
             ((region, sex, d) for region, sexes in frozen["self_employment_monthly_coefficients"].items()
              for sex in sexes for d in plan["offsets_soum"]), "tax")
    coverage(extension["conditional_remittance_cases"],
             lambda r: (r["comparison_period_interpretation"], r["country_group"],
                        None if r["offset_soum"] is None else integer(r["offset_soum"])),
             ((period, group, d) for period in plan["remittance_interpretations"]
              for group in plan["remittance_imputation_multiples"] for d in [*plan["offsets_soum"], None]), "remittance")
    coverage(extension["goat_cases"], lambda r: integer(r["goats"]), plan["goat_counts"], "goat")
    coverage(data["income_boundary_cases"],
             lambda r: (r["boundary_multiple"], integer(r["offset_soum"]), boolean(r["former_primary"])),
             [(a, d, False) for a in frozen["boundary_multiples"] for d in frozen["boundary_offsets_soum"]]
             + [("1", 0, True)], "income")
    for row in data["income_boundary_cases"]:
        income = p * Fraction(row["boundary_multiple"]) + row["offset_soum"]
        check(Fraction(row["income_soum"]) == income)
        expected = {
            "paragraph_33a_primary_income_refusal": income > p,
            "paragraph_32_primary_recognition_when_no_other_refusal": income <= p,
            "paragraph_39b_primary_income_condition": income < p,
            "paragraph_39v_former_primary_borderline_condition": row["former_primary"] and p <= income <= 3*p/2,
            "paragraph_33_registry_income_refusal": income > 2*p,
            "primary_recognition_and_category_predicates_disagree": income == p,
        }
        check(all(type(value) is bool for value in row["predicates"].values()))
        check(row["predicates"] == expected, "Income predicate disagreement")
    check(Fraction(data["official_example_check"]["computed_monthly_per_person_soum"]) == Fraction(6480000,15))
    counts = {}
    for row in extension["land_integer_grid"]:
        u, b = integer(row["total_m2"], allow_string=True), integer(row["buildings_m2"], allow_string=True)
        # Equivalent piecewise formula, independent of the implementation's min expression.
        area = Fraction(4*u,5)-b if u <= 1000 else Fraction(u-b-200)
        check(area == Fraction(row["literal_area_m2"]))
        check((5*b > 4*u if u <= 1000 else b > u-200) == boolean(row["negative_literal_area"]))
        check(Fraction(row["literal_monthly_normative_income_soum"]) == area*476)
        counts[u] = counts.get(u,0)+int(area<0)
    check(counts == {100:20,1000:200,1001:200,2000:200})
    for row in extension["hardship_boundary_cases"]:
        d = Fraction(row["ordinary_income_soum"])
        check(d == p * Fraction(row["boundary_multiple"]) + row["offset_soum"])
        check(row["special_route_income_conditions"] == (p < d <= 2*p))
        check(row["special_route_excluded_by_ordinary_interval"] == (3*p/2 < d <= 2*p))
        check(row["special_route_excluded_by_adjusted_interval"] == (p < d < 4*p/3))
    for row in extension["tax_floor_cases"]:
        t, base = Fraction(row["tax_total_three_months_soum"]), Fraction(row["base_monthly_soum"])
        check(base == m * Fraction(frozen["self_employment_monthly_coefficients"][row["region_class"]][row["sex"]]))
        check(t == 6*base/5 + row["offset_soum"])
        expected = base if 5*t <= 6*base else 5*t/6
        check(Fraction(row["monthly_normative_income_soum"]) == expected)
    for row in extension["conditional_remittance_cases"]:
        q = row["reported_comparison_value_soum"]
        check((q is None and row["offset_soum"] is None) or
              (q is not None and row["offset_soum"] is not None and Fraction(q) == 2*m + row["offset_soum"]))
        impute = q is None or Fraction(q)<2*m
        coefficient = 3 if row["country_group"]=="listed_countries" else 2
        divisor = 1 if row["comparison_period_interpretation"]=="monthly" else 3
        expected = coefficient*m if impute else Fraction(q)/divisor
        check(boolean(row["imputation_applied"])==impute)
        check(Fraction(row["monthly_contribution_soum"])==expected)
    for row in extension["goat_cases"]:
        count = row["goats"]
        # Independent integer threshold and excess numerator.
        expected = Fraction((7*count-100)*m,200) if 7*count>100 else Fraction(0)
        check(Fraction(row["monthly_normative_income_soum"])==expected)
    result = {"verified": True,
              "method": "Independent piecewise and integer inequalities; no imported rule functions",
              "frozen_case_inventory_verified": True,
              "income_cases_checked": len(data["income_boundary_cases"]),
              "land_cases_checked": len(extension["land_integer_grid"]),
              "negative_land_cases_by_plot": counts,
              "hardship_cases_checked": len(extension["hardship_boundary_cases"]),
              "tax_cases_checked": len(extension["tax_floor_cases"]),
              "conditional_remittance_cases_checked": len(extension["conditional_remittance_cases"]),
              "goat_cases_checked": len(extension["goat_cases"]),
              "audit_sha256": hashlib.sha256(tested_bytes).hexdigest(),
              "input_mode": "saved report bytes" if from_file else "in-memory canonical JSON",
              "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "command": "python scripts/verify_results.py" if from_file else None}
    if write_output:
        (ROOT/"results/audit/independent_check.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result,indent=2))
    return result


if __name__=="__main__":
    verify()
