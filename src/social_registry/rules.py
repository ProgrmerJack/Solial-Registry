"""Published-rule audit; normalized frozen inputs are in data/rules/."""
from fractions import Fraction
import json
from pathlib import Path
from .numeric import number, require

ROOT = Path(__file__).resolve().parents[2]
LEGAL_SPEC = json.loads((ROOT / "data/rules/legal_specification.json").read_text())

def monthly_per_person(total, members, months=3):
    require(type(members) is int and members > 0, "invalid household size")
    require(type(months) is int and months > 0, "invalid number of months")
    return number(total) / members / months


def income_predicates(income, poverty_line, former_primary=False):
    income, poverty_line = number(income), number(poverty_line)
    require(poverty_line > 0, "invalid poverty line")
    require(type(former_primary) is bool, "invalid prior-category state")
    primary_refusal = income > poverty_line
    primary_category = income < poverty_line
    return {
        "paragraph_33a_primary_income_refusal": primary_refusal,
        "paragraph_32_primary_recognition_when_no_other_refusal": not primary_refusal,
        "paragraph_39b_primary_income_condition": primary_category,
        "paragraph_39v_former_primary_borderline_condition": (
            former_primary and poverty_line <= income <= poverty_line * Fraction(3, 2)),
        "paragraph_33_registry_income_refusal": income > poverty_line * 2,
        "primary_recognition_and_category_predicates_disagree": (
            not primary_refusal and not primary_category),
    }


def land_calculation(total_m2, buildings_m2, remuneration, local_coefficient):
    total_m2, buildings_m2, remuneration, local_coefficient = map(
        number, (total_m2, buildings_m2, remuneration, local_coefficient))
    require(0 <= buildings_m2 <= total_m2, "invalid area geometry")
    require(remuneration > 0 and local_coefficient > 0, "invalid income parameters")
    deduction = min(total_m2 * number(LEGAL_SPEC["area_fraction_deducted"]),
                    number(LEGAL_SPEC["area_deduction_cap_m2"]))
    literal_area = total_m2 - buildings_m2 - deduction
    income_factor = number(LEGAL_SPEC["land_income_coefficient_per_100_m2"]) * remuneration * local_coefficient / 100
    return {
        "total_m2": str(total_m2), "buildings_m2": str(buildings_m2),
        "deduction_m2": str(deduction), "literal_area_m2": str(literal_area),
        "literal_monthly_normative_income_soum": str(literal_area * income_factor),
        "negative_literal_area": literal_area < 0,
        "proposed_zero_floor_area_m2": str(max(literal_area, 0)),
        "proposed_zero_floor_monthly_income_soum": str(max(literal_area, 0) * income_factor),
    }


def hardship_review_check():
    case = LEGAL_SPEC["review_counterexample"]
    poverty = number(LEGAL_SPEC["minimum_consumption_monthly_per_person_soum"])
    ordinary = monthly_per_person(case["three_month_total_soum"], case["members"], case["months"])
    adjusted = ordinary * number(case["hardship_adjustment"])
    return {
        "selection": case["selection"], "assumptions": case["assumptions"],
        "ordinary_monthly_per_person_soum": str(ordinary),
        "adjusted_monthly_per_person_soum": str(adjusted),
        "ordinary_income_above_primary_threshold": ordinary > poverty,
        "paragraph_35b_hardship_upper_bound_satisfied": adjusted <= poverty * Fraction(3, 2),
        "abandoned_blanket_borderline_lower_bound_satisfied": adjusted > poverty,
        "interpretation": "Demonstrates a conflict in the abandoned amendment. Revised branch preserves paragraph 35 hardship criteria; no measured household outcome."}


def hardship_predicates(income, poverty):
    income, poverty = number(income), number(poverty)
    require(income >= 0 and poverty > 0, "invalid income parameters")
    adjusted = income * Fraction(3, 4)
    special = income > poverty and adjusted <= poverty * Fraction(3, 2)
    raw_common = poverty <= income <= poverty * Fraction(3, 2)
    adjusted_common = poverty <= adjusted <= poverty * Fraction(3, 2)
    return {"ordinary_income_soum": str(income), "adjusted_income_soum": str(adjusted),
            "special_route_income_conditions": special,
            "general_interval_using_ordinary_income": raw_common,
            "general_interval_using_adjusted_income": adjusted_common,
            "special_route_excluded_by_ordinary_interval": special and not raw_common,
            "special_route_excluded_by_adjusted_interval": special and not adjusted_common}


def remittance_monthly(reported, remuneration, imputation_multiple, interpretation):
    """Conditional diagnostic: the comparison period is NOT resolved in the act."""
    wage = number(remuneration)
    require(wage > 0 and imputation_multiple in (2, 3), "invalid remittance parameters")
    require(interpretation in ("monthly", "three_month_total"), "unknown period")
    value = None if reported is None else number(reported)
    require(value is None or value >= 0, "negative remittance")
    imputed = value is None or value < 2 * wage
    monthly = (imputation_multiple * wage if imputed else
               value / (1 if interpretation == "monthly" else 3))
    return {"reported_comparison_value_soum": None if value is None else str(value),
            "comparison_period_interpretation": interpretation,
            "imputation_applied": imputed, "monthly_contribution_soum": str(monthly)}


def tax_normative_monthly(tax_total_three_months, base_monthly):
    total, base = number(tax_total_three_months), number(base_monthly)
    require(total >= 0 and base > 0, "invalid tax parameters")
    multiplier = number(LEGAL_SPEC["extension_prespecified_inputs"]["tax_income_multiplier"])
    return max(multiplier * total / 3, base)


def goat_normative_monthly(count, remuneration):
    require(type(count) is int and count >= 0, "invalid animal count")
    wage = number(remuneration)
    require(wage > 0, "invalid remuneration")
    spec = LEGAL_SPEC["extension_prespecified_inputs"]
    equivalent = count * number(spec["goat_conversion"])
    chargeable = max(equivalent - spec["animal_exempt_equivalent_heads"], 0)
    return {"goats": count, "equivalent_heads": str(equivalent),
            "chargeable_equivalent_heads": str(chargeable),
            "monthly_normative_income_soum": str(chargeable * wage * number(
                spec["animal_income_remuneration_multiple"]))}


def extended_audit(poverty, wage):
    spec = LEGAL_SPEC["extension_prespecified_inputs"]
    grid, summaries = [], []
    for total in spec["land_total_areas_m2"]:
        rows = [land_calculation(total, building, str(wage), 1)
                for building in range(total + 1)]
        grid.extend(rows)
        minimum = min(number(x["literal_area_m2"]) for x in rows)
        summaries.append({"total_m2": total, "constructed_cases": len(rows),
                          "negative_area_cases": sum(x["negative_literal_area"] for x in rows),
                          "minimum_literal_area_m2": str(minimum),
                          "maximum_zero_floor_monthly_income_change_soum": str(
                              -minimum * wage * Fraction(35, 1000) / 100)})
    hardships = []
    for multiple in spec["hardship_boundary_multiples"]:
        for offset in spec["offsets_soum"]:
            row = hardship_predicates(str(poverty * number(multiple) + offset), str(poverty))
            row.update(boundary_multiple=multiple, offset_soum=offset)
            hardships.append(row)
    remittances, jumps = [], []
    for interpretation in spec["remittance_interpretations"]:
        for group, multiple in spec["remittance_imputation_multiples"].items():
            for offset in [-1, 0, 1, None]:
                q = None if offset is None else str(2 * wage + offset)
                row = remittance_monthly(q, str(wage), multiple, interpretation)
                row.update(country_group=group, offset_soum=offset)
                remittances.append(row)
            before = number(remittance_monthly(str(2 * wage - 1), str(wage), multiple,
                                              interpretation)["monthly_contribution_soum"])
            at = number(remittance_monthly(str(2 * wage), str(wage), multiple,
                                          interpretation)["monthly_contribution_soum"])
            jumps.append({"interpretation": interpretation, "country_group": group,
                          "drop_at_comparison_threshold_monthly_soum": str(before - at),
                          "drop_per_person_four_members_soum": str((before - at) / 4)})
    taxes, informal = [], []
    for region, sexes in LEGAL_SPEC["self_employment_monthly_coefficients"].items():
        for sex, coefficient in sexes.items():
            base = number(coefficient) * wage
            crossover = base * 3 / number(spec["tax_income_multiplier"])
            for offset in spec["offsets_soum"]:
                total = crossover + offset
                taxes.append({"region_class": region, "sex": sex,
                              "base_monthly_soum": str(base), "tax_crossover_three_month_total_soum": str(crossover),
                              "offset_soum": offset, "tax_total_three_months_soum": str(total),
                              "monthly_normative_income_soum": str(tax_normative_monthly(str(total), str(base)))})
            informal.append({"region_class": region, "sex": sex, "base_monthly_soum": str(base),
                             "informal_monthly_soum": str(base * number(spec["informal_income_multiplier"]))})
    return {"land_integer_grid": grid, "land_grid_summary": summaries,
            "hardship_boundary_cases": hardships, "conditional_remittance_cases": remittances,
            "conditional_remittance_threshold_drops": jumps, "tax_floor_cases": taxes,
            "informal_income_cases": informal,
            "goat_cases": [goat_normative_monthly(n, str(wage)) for n in spec["goat_counts"]],
            "scope": "Deterministic constructed cases. Remittance branches are conditional, not an adopted interpretation; hardship predicates assume valid recommendation, quota and other statutory conditions."}


def legal_audit():
    example = LEGAL_SPEC["official_example"]
    calculated = monthly_per_person(example["three_month_total_soum"],
                                    example["members"], example["months"])
    poverty = number(LEGAL_SPEC["minimum_consumption_monthly_per_person_soum"])
    wage = number(LEGAL_SPEC["minimum_remuneration_monthly_soum"])
    boundary_cases = []
    for multiple in LEGAL_SPEC["boundary_multiples"]:
        for offset in LEGAL_SPEC["boundary_offsets_soum"]:
            income = poverty * number(multiple) + offset
            boundary_cases.append({"boundary_multiple": multiple,
                                   "offset_soum": offset, "income_soum": str(income),
                                   "former_primary": False,
                                   "predicates": income_predicates(str(income), str(poverty))})
    boundary_cases.append({"boundary_multiple": "1", "offset_soum": 0,
                           "income_soum": str(poverty), "former_primary": True,
                           "predicates": income_predicates(str(poverty), str(poverty), True)})
    land_cases = [land_calculation(a, b, str(wage),
                  LEGAL_SPEC["assumed_diagnostic_local_tax_coefficient"])
                  for a, b in LEGAL_SPEC["area_cases_m2"]]
    coefficients = []
    for region, row in LEGAL_SPEC["self_employment_monthly_coefficients"].items():
        male, female = (number(row[k]) * wage for k in ("male", "female"))
        coefficients.append({"region_class": region, "male_coefficient": row["male"],
                             "female_coefficient": row["female"],
                             "male_monthly_normative_income_soum": str(male),
                             "female_monthly_normative_income_soum": str(female),
                             "monthly_difference_soum": str(male - female),
                             "per_person_monthly_contribution_difference_four_members_soum": str(
                                 monthly_per_person(str(male - female), 4, 1))})
    return {
        "analysis_kind": "published_legal_rule_audit",
        "rule_extraction_and_prespecified_inputs": LEGAL_SPEC,
        "official_example_check": {
            "computed_monthly_per_person_soum": str(calculated),
            "difference_from_published_soum": str(calculated - example["published_result_soum"]),
            "interpretation": "Published illustrative benchmark, not an observed household."},
        "income_boundary_cases": boundary_cases,
        "land_cases": land_cases,
        "self_employment_coefficient_comparison": coefficients,
        "post_hoc_review_counterexample": hardship_review_check(),
        "extended_analysis": extended_audit(poverty, wage),
        "scope_limits": [
            "No actual household observations, targeting accuracy, prevalence or fiscal effects.",
            "No 2027 weights supplied; this is not a validation of that model.",
            "No whole-registry eligibility engine or official operational rounding rule.",
            "Land cases satisfy only the declared algebraic domain; local coefficient 1 is assumed, not measured.",
            "Zero-floor outputs are proposals, not the current literal formula.",
            "Monthly remuneration calculations use September 2026 rate only, not retrospective three-month histories.",
            "The encoded male/female difference is a normative-income sensitivity, not measured discrimination.",
        ],
        "unresolved_specification_questions": [
            "Paragraph 18 reference-month inclusivity: paragraph 30 uses May-July for a September application.",
            "Paragraph 26 remittance-comparison period and units must be explicit before executable replay.",
            "Negative-area prevention or cadastral domain restrictions in the actual system require confirmation.",
            "Boundary remedy must reconcile PF-258 paragraph 3 and Annex 1 notes with Resolution 35 paragraphs 34-35 and 39, not silently override the decree or hardship route.",
        ],
    }


