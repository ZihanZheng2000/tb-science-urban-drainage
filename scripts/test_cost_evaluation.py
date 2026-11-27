"""Unit tests for feasibility-first economic evaluation, without running SWMM."""
from pathlib import Path
import importlib.util
import json
import unittest

TASK = Path(__file__).resolve().parents[1] / "tasks/engineering-sciences/civil-engineering/tecnopolo-drainage-retrofit"
SPEC = importlib.util.spec_from_file_location("cost_economics", TASK / "tests/economics.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CRITERIA = json.loads((TASK / "tests/private/cost_criteria.json").read_text())


class FeasibilityFirstCostChecks(unittest.TestCase):
    def evaluate(self, cost, **changes):
        status = {"hydraulic_pass": True, "prediction_pass": True, "basis_pass": True}
        status.update(changes)
        return MODULE.evaluate_cost({"lifecycle_CU": cost}, criteria=CRITERIA, **status)

    def test_cheaper_feasible_design_has_better_comparison_value(self):
        cheap = self.evaluate(1_300_000)
        expensive = self.evaluate(1_400_000)
        self.assertLess(cheap["comparison_value_CU"], expensive["comparison_value_CU"])

    def test_infeasible_cheap_design_cannot_enter_cost_comparison(self):
        result = self.evaluate(100_000, hydraulic_pass=False)
        self.assertFalse(result["eligible_for_cost_comparison"])
        self.assertIsNone(result["comparison_value_CU"])
        self.assertIsNone(result["cost_quality_passed"])

    def test_bad_prediction_prevents_cost_comparison(self):
        self.assertFalse(self.evaluate(100_000, prediction_pass=False)["eligible_for_cost_comparison"])

    def test_wrong_basis_prevents_cost_comparison(self):
        self.assertFalse(self.evaluate(100_000, basis_pass=False)["eligible_for_cost_comparison"])

    def test_feasible_expensive_design_keeps_cost_for_comparison(self):
        value = CRITERIA["maximum_accepted_lifecycle_CU"] + 1000
        result = self.evaluate(value)
        self.assertTrue(result["eligible_for_cost_comparison"])
        self.assertEqual(result["comparison_value_CU"], value)
        self.assertFalse(result["cost_quality_passed"])

    def test_private_acceptance_boundary(self):
        self.assertTrue(self.evaluate(CRITERIA["maximum_accepted_lifecycle_CU"])["cost_quality_passed"])


if __name__ == "__main__":
    unittest.main()
