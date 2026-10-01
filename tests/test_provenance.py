"""Publication must reject modified or stale outputs, not trust their labels."""
import json
import importlib.util
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from social_registry.provenance import validated_audit, code_fingerprint

ROOT = Path(__file__).resolve().parents[1]
module_spec = importlib.util.spec_from_file_location("independent_verifier", ROOT / "scripts/verify_results.py")
independent = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(independent)


class ProvenanceTests(unittest.TestCase):
    def check_mutation(self, mutate):
        data = json.loads((ROOT / "results/audit/legal_rule_audit.json").read_text())
        mutate(data)
        with tempfile.TemporaryDirectory(prefix="registry-provenance-") as folder:
            path = Path(folder) / "modified.json"
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                validated_audit(path)

    def test_real_output_replays(self):
        data = validated_audit(ROOT / "results/audit/legal_rule_audit.json")
        self.assertEqual(data["reproducibility"]["code_sha256"], code_fingerprint())

    def test_tampered_result_rejected(self):
        self.check_mutation(lambda data: data["official_example_check"].update(
            computed_monthly_per_person_soum="432001"))

    def test_stale_code_hash_rejected(self):
        self.check_mutation(lambda data: data["reproducibility"].update(code_sha256="stale"))

    def test_stale_input_hash_rejected(self):
        self.check_mutation(lambda data: data["reproducibility"].update(input_sha256="stale"))

    def test_independent_inventory_accepts_real_output(self):
        data = json.loads((ROOT / "results/audit/legal_rule_audit.json").read_text())
        result = independent.verify(data, write_output=False)
        self.assertTrue(result["frozen_case_inventory_verified"])
        self.assertEqual(result["income_cases_checked"], 10)

    def test_independent_verifier_rejects_empty_grids(self):
        original = json.loads((ROOT / "results/audit/legal_rule_audit.json").read_text())
        for field in ["land_integer_grid", "hardship_boundary_cases", "tax_floor_cases",
                      "conditional_remittance_cases", "goat_cases"]:
            with self.subTest(field=field):
                data = deepcopy(original)
                data["extended_analysis"][field] = []
                with self.assertRaises(ValueError):
                    independent.verify(data, write_output=False)

    def test_independent_verifier_rejects_duplicate_case_at_same_count(self):
        data = json.loads((ROOT / "results/audit/legal_rule_audit.json").read_text())
        rows = data["extended_analysis"]["hardship_boundary_cases"]
        rows[0] = deepcopy(rows[1])
        with self.assertRaises(ValueError):
            independent.verify(data, write_output=False)

    def test_independent_verifier_rejects_changed_equality_predicate(self):
        data = json.loads((ROOT / "results/audit/legal_rule_audit.json").read_text())
        row = next(r for r in data["income_boundary_cases"] if r["boundary_multiple"] == "1"
                   and r["offset_soum"] == 0 and not r["former_primary"])
        row["predicates"]["paragraph_39b_primary_income_condition"] = True
        with self.assertRaises(ValueError):
            independent.verify(data, write_output=False)

    def test_independent_verifier_rejects_relabelled_inputs(self):
        data = json.loads((ROOT / "results/audit/legal_rule_audit.json").read_text())
        data["extended_analysis"]["hardship_boundary_cases"][0]["ordinary_income_soum"] = "715000"
        with self.assertRaises(ValueError):
            independent.verify(data, write_output=False)

    def test_independent_verifier_rejects_coerced_case_inputs(self):
        original = json.loads((ROOT / "results/audit/legal_rule_audit.json").read_text())
        for field, value in [("total_m2", "100.5"), ("buildings_m2", "0.5")]:
            with self.subTest(field=field):
                data = deepcopy(original)
                row = next(r for r in data["extended_analysis"]["land_integer_grid"]
                           if r["total_m2"] == "100" and r["buildings_m2"] == "0")
                row[field] = value
                with self.assertRaises(ValueError):
                    independent.verify(data, write_output=False)
        data = deepcopy(original)
        next(r for r in data["extended_analysis"]["goat_cases"] if r["goats"] == 1)["goats"] = True
        with self.assertRaises(ValueError):
            independent.verify(data, write_output=False)
