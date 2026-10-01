"""Boundary, invalid-input, unit and independent-algebra regression tests."""
from fractions import Fraction
from copy import deepcopy
import json,unittest
from pathlib import Path
from social_registry.numeric import number
from social_registry.additive import config,calculate,evaluate
from social_registry.rules import (monthly_per_person,income_predicates,land_calculation,legal_audit,hardship_review_check,extended_audit,hardship_predicates,remittance_monthly,remittance_monthly_proposed,tax_normative_monthly,goat_normative_monthly)
DEMO=json.loads((Path(__file__).resolve().parents[1]/"data/fixtures/additive_demo.json").read_text())

class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.prepared = config(DEMO["config"])

    def test_threshold_equality_and_both_sides(self):
        for score, expected in [("999/100", 0), ("10", 1), ("1001/100", 1),
                                ("1999/100", 1), ("20", 2), ("2001/100", 2)]:
            result = calculate(self.prepared, {"test_a": score, "test_b": "0"})
            self.assertEqual(result["category"], f"test_category_{expected}")

    def test_missing_is_not_zero(self):
        zero = calculate(self.prepared, {"test_a": "0", "test_b": "0"})
        missing = calculate(self.prepared, {"test_a": None, "test_b": "0"})
        self.assertFalse(zero["needs_review"])
        self.assertIsNone(missing["category"])
        self.assertEqual(len(missing["possible_categories"]), 3)

    def test_negative_weight_interval(self):
        result = calculate(self.prepared, {"test_a": "11", "test_b": None})
        # Independent endpoints: 11 - 4/2 = 9; 11 - 0/2 = 11.
        self.assertEqual((result["score_lower"], result["score_upper"]), ("9", "11"))
        self.assertEqual(result["possible_categories"], ["test_category_0", "test_category_1"])

    def test_degenerate_missing_range_still_requires_review(self):
        raw = deepcopy(DEMO["config"])
        raw["variables"][0]["max"] = "0"
        result = calculate(config(raw), {"test_a": None, "test_b": "0"})
        self.assertTrue(result["needs_review"])
        self.assertIsNone(result["category"])

    def test_exact_decimal_arithmetic(self):
        raw = {"version": "test", "variables": [
            {"name": "x", "weight": "0.1", "min": "0", "max": "3"}],
            "thresholds": ["0.3"], "labels": ["below", "at_or_above"]}
        result = calculate(config(raw), {"x": "3"})
        self.assertEqual(result["score_lower"], "3/10")
        self.assertEqual(result["category"], "at_or_above")

    def test_invalid_numbers_rejected(self):
        for bad in [True, 1.0, "NaN", "Infinity", "1/0", "garbage", {}, []]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                number(bad)

    def test_invalid_config_rejected(self):
        for mutation in [lambda p: p.update(thresholds=["20", "10"]),
                         lambda p: p.update(thresholds=["10", "10"]),
                         lambda p: p["variables"][0].update(min="31"),
                         lambda p: p["variables"].append(deepcopy(p["variables"][0])),
                         lambda p: p.update(labels=["duplicate"] * 3),
                         lambda p: p.update(extra="unknown")]:
            raw = deepcopy(DEMO["config"])
            mutation(raw)
            with self.assertRaises(ValueError):
                config(raw)

    def test_invalid_rows_rejected(self):
        for values in [{"test_a": "31", "test_b": "0"}, {"test_a": "1"},
                       {"test_a": "1", "test_b": "0", "extra": 1}]:
            with self.assertRaises(ValueError):
                calculate(self.prepared, values)

    def test_duplicate_ids_and_unknown_reference_rejected(self):
        raw = deepcopy(DEMO)
        raw["records"].append(deepcopy(raw["records"][0]))
        with self.assertRaises(ValueError):
            evaluate(raw)
        raw = deepcopy(DEMO)
        raw["records"][0]["reference_category"] = "not-a-category"
        with self.assertRaises(ValueError):
            evaluate(raw)

    def test_empty_records_rejected(self):
        raw = deepcopy(DEMO)
        raw["records"] = []
        with self.assertRaises(ValueError):
            evaluate(raw)

    def test_no_comparable_reference_has_no_rate(self):
        raw = deepcopy(DEMO)
        raw["records"] = [raw["records"][4]]
        result = evaluate(raw)
        self.assertEqual(result["counts"]["reference_comparable"], 0)
        self.assertIsNone(result["reference_category_mismatch_fraction"])

    def test_wrong_reference_is_detected(self):
        raw = deepcopy(DEMO)
        raw["records"][0]["reference_category"] = "test_category_2"
        result = evaluate(raw)
        self.assertEqual(result["counts"]["reference_mismatches"], 1)
        self.assertEqual(result["reference_category_mismatch_fraction"], "1/4")

    def test_hand_derived_demo_counts(self):
        result = evaluate(DEMO)
        self.assertEqual(result["counts"], {
            "records": 7, "complete": 5, "unresolved": 2,
            "multi_category_intervals": 2, "reference_comparable": 4,
            "reference_mismatches": 0, "reference_excluded_unresolved": 1,
            "no_reference": 2})

    def test_official_published_income_example(self):
        self.assertEqual(monthly_per_person(6480000, 5), 432000)

    def test_invalid_divisors_rejected(self):
        for members, months in [(0, 3), (-1, 3), (True, 3), (5, 0), (5, 1.0)]:
            with self.assertRaises(ValueError):
                monthly_per_person(6480000, members, months)

    def test_official_income_equality_gap(self):
        at = income_predicates(715000, 715000)
        self.assertFalse(at["paragraph_33a_primary_income_refusal"])
        self.assertFalse(at["paragraph_39b_primary_income_condition"])
        self.assertTrue(at["primary_recognition_and_category_predicates_disagree"])
        for value in (714999, 715001):
            self.assertFalse(income_predicates(value, 715000)[
                "primary_recognition_and_category_predicates_disagree"])

    def test_former_category_control_and_refusal_boundary(self):
        for value, expected in [(714999, False), (715000, True),
                                (1072500, True), (1072501, False)]:
            self.assertEqual(income_predicates(value, 715000, True)[
                "paragraph_39v_former_primary_borderline_condition"], expected)
        self.assertFalse(income_predicates(1430000, 715000)["paragraph_33_registry_income_refusal"])
        self.assertTrue(income_predicates(1430001, 715000)["paragraph_33_registry_income_refusal"])

    def test_literal_negative_land_separate_from_proposal(self):
        result = land_calculation(100, 90, 1360000, 1)
        self.assertEqual(result["literal_area_m2"], "-10")
        self.assertEqual(result["literal_monthly_normative_income_soum"], "-4760")
        self.assertEqual(result["proposed_zero_floor_area_m2"], "0")

    def test_area_cap_boundary(self):
        # Independent algebra: below cap 0.8*UM-QM; above cap UM-QM-200.
        for area, expected in [(999, "999/5"), (1000, "200"), (1001, "200")]:
            self.assertEqual(land_calculation(area, 0, 1360000, 1)["deduction_m2"], expected)
        self.assertEqual(land_calculation(2000, 0, 1360000, 1)["literal_area_m2"], "1800")

    def test_bad_geometry_and_parameters_rejected(self):
        for a, b, wage, k in [(100, 101, 1360000, 1), (100, -1, 1360000, 1),
                              (-1, 0, 1360000, 1), (100, 0, 0, 1), (100, 0, 1360000, 0)]:
            with self.assertRaises(ValueError):
                land_calculation(a, b, wage, k)

    def test_legal_audit_scope_and_coefficient_units(self):
        audit = legal_audit()
        self.assertEqual(len(audit["income_boundary_cases"]), 10)
        self.assertEqual(len(audit["land_cases"]), 9)
        self.assertEqual(sum(x["negative_literal_area"] for x in audit["land_cases"]), 3)
        for row in audit["self_employment_coefficient_comparison"]:
            self.assertEqual(row["monthly_difference_soum"], "544000")
            self.assertEqual(row["per_person_monthly_contribution_difference_four_members_soum"], "136000")

    def test_review_hardship_counterexample(self):
        result = hardship_review_check()
        self.assertEqual(result["ordinary_monthly_per_person_soum"], "2860000/3")
        self.assertEqual(result["adjusted_monthly_per_person_soum"], "715000")
        self.assertTrue(result["ordinary_income_above_primary_threshold"])
        self.assertTrue(result["paragraph_35b_hardship_upper_bound_satisfied"])
        self.assertFalse(result["abandoned_blanket_borderline_lower_bound_satisfied"])

    def test_complete_land_grid_and_independent_negative_count(self):
        extension = extended_audit(Fraction(715000), Fraction(1360000))
        self.assertEqual(len(extension["land_integer_grid"]), 4105)
        self.assertEqual([r["negative_area_cases"] for r in extension["land_grid_summary"]],
                         [20, 200, 200, 200])
        for row in extension["land_integer_grid"]:
            u, b = int(row["total_m2"]), int(row["buildings_m2"])
            independent_negative = 5*b > 4*u if u <= 1000 else b > u-200
            self.assertEqual(row["negative_literal_area"], independent_negative)

    def test_hardship_exact_intervals(self):
        p = Fraction(715000)
        for income, special, raw, adjusted in [(p, False, True, False),
                (p+1, True, True, False), (4*p/3, True, True, True),
                (3*p/2, True, True, True), (3*p/2+1, True, False, True),
                (2*p, True, False, True), (2*p+1, False, False, False)]:
            r = hardship_predicates(str(income), str(p))
            self.assertEqual((r["special_route_income_conditions"],
                              r["general_interval_using_ordinary_income"],
                              r["general_interval_using_adjusted_income"]), (special, raw, adjusted))

    def test_conditional_remittance_discontinuities(self):
        m = 1360000
        for period, multiple, expected in [("monthly", 3, Fraction(m)),
                ("monthly", 2, Fraction(0)), ("three_month_total", 3, Fraction(7*m,3)),
                ("three_month_total", 2, Fraction(4*m,3))]:
            before = remittance_monthly(2*m-1, m, multiple, period)
            at = remittance_monthly(2*m, m, multiple, period)
            self.assertTrue(before["imputation_applied"])
            self.assertFalse(at["imputation_applied"])
            self.assertEqual(number(before["monthly_contribution_soum"])-number(at["monthly_contribution_soum"]), expected)
            self.assertTrue(remittance_monthly(None, m, multiple, period)["imputation_applied"])

    def test_proposed_remittance_rule_is_monotone(self):
        m = 1360000
        for multiple in (2, 3):
            self.assertEqual(remittance_monthly_proposed(None, m, multiple), multiple*m)
            self.assertEqual(remittance_monthly_proposed(multiple*m-1, m, multiple), multiple*m)
            self.assertEqual(remittance_monthly_proposed(multiple*m+1, m, multiple), multiple*m+1)
            vals = [remittance_monthly_proposed(q, m, multiple) for q in range(0, 4*m+1, 1000)]
            self.assertEqual(vals, sorted(vals))
        # The current monthly reading is not monotone for listed countries: more remittance, less income.
        current = [number(remittance_monthly(q, m, 3, "monthly")["monthly_contribution_soum"])
                   for q in range(0, 4*m+1, 1000)]
        self.assertNotEqual(current, sorted(current))
        with self.assertRaises(ValueError):
            remittance_monthly_proposed(-1, m, 3)

    def test_hardship_route_conflicts_under_both_interval_readings(self):
        # Paragraphs 34-35 admit D=1.2P and D=1.8P; paragraph 39(v) excludes one under each reading.
        p = 715000
        ordinary_excluded = hardship_predicates("1287000", str(p))
        adjusted_excluded = hardship_predicates("858000", str(p))
        self.assertTrue(ordinary_excluded["special_route_excluded_by_ordinary_interval"])
        self.assertTrue(adjusted_excluded["special_route_excluded_by_adjusted_interval"])

    def test_tax_floor_and_monotonicity(self):
        # Independent crossover: with base 100, 120 of tax over three months.
        self.assertEqual(tax_normative_monthly(119, 100), 100)
        self.assertEqual(tax_normative_monthly(120, 100), 100)
        self.assertEqual(tax_normative_monthly(121, 100), Fraction(605,6))
        vals = [tax_normative_monthly(n, 100) for n in range(241)]
        self.assertEqual(vals, sorted(vals))

    def test_goat_fractional_exemption(self):
        expected = {0: "0", 1: "0", 14: "0", 15: "34000", 20: "272000", 100: "4080000"}
        for count, income in expected.items():
            self.assertEqual(goat_normative_monthly(count, 1360000)["monthly_normative_income_soum"], income)
        for count in [-1, True, "15", 1.5]:
            with self.assertRaises(ValueError):
                goat_normative_monthly(count, 1360000)


