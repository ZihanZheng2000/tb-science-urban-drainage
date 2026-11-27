"""Synthetic evidence tests for the CI result checker, not container trial results."""
from pathlib import Path
import json
import tempfile
import unittest

from check_harbor_results import validate


class HarborResultChecks(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / "validation/parser-unit-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.job = Path(self.temporary.name)
        self.trial = self.job / "trial"
        self.verifier = self.trial / "verifier"
        self.verifier.mkdir(parents=True)

    def tearDown(self):
        self.temporary.cleanup()

    def write_json(self, path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def prepare(self, agent="oracle"):
        reward = 1 if agent == "oracle" else 0
        (self.verifier / "reward.txt").write_text(str(reward))
        self.write_json(self.trial / "result.json", {
            "exception_info": None, "verifier_environment_mode": "separate",
            "agent_info": {"name": agent}, "verifier_result": {"rewards": {"reward": reward}}})
        status = "passed" if reward == 1 else "failed"
        self.write_json(self.verifier / "ctrf.json", {"results": {
            "tests": [{"name": f"check_{i}", "status": status} for i in range(5)],
            "summary": {"tests": 5, "passed": 5 if reward else 0, "failed": 0 if reward else 5,
                        "skipped": 0, "pending": 0, "other": 0}}})
        if reward:
            self.write_json(self.verifier / "stress_results.json",
                            [{"id": f"case_{i}", "violations": []} for i in range(48)])
            self.write_json(self.verifier / "costs.json", {"lifecycle_CU": 1_420_382.17})
            self.write_json(self.verifier / "prediction.json",
                            {"observation_scale_rmse": [{"rmse_in_noise_sd": .5} for _ in range(12)]})

    def test_accepts_consistent_oracle_evidence(self):
        self.prepare()
        self.assertTrue(validate(self.job, 1, "oracle")["passed"])

    def test_accepts_nop_scientific_failure(self):
        self.prepare("nop")
        self.assertTrue(validate(self.job, 0, "nop")["passed"])

    def test_rejects_missing_reward(self):
        with self.assertRaises(AssertionError):
            validate(self.job, 1, "oracle")

    def test_rejects_infrastructure_failure(self):
        self.prepare("nop")
        path = self.trial / "result.json"
        result = json.loads(path.read_text())
        result["exception_info"] = {"exception_type": "EnvironmentBuildError"}
        self.write_json(path, result)
        with self.assertRaises(AssertionError):
            validate(self.job, 0, "nop")

    def test_rejects_shared_verification(self):
        self.prepare()
        path = self.trial / "result.json"
        result = json.loads(path.read_text())
        result["verifier_environment_mode"] = "shared"
        self.write_json(path, result)
        with self.assertRaises(AssertionError):
            validate(self.job, 1, "oracle")

    def test_rejects_inconsistent_ctrf(self):
        self.prepare()
        path = self.verifier / "ctrf.json"
        result = json.loads(path.read_text())
        result["results"]["summary"]["passed"] = 4
        self.write_json(path, result)
        with self.assertRaises(AssertionError):
            validate(self.job, 1, "oracle")

    def test_rejects_failed_hydraulics_despite_positive_reward(self):
        self.prepare()
        path = self.verifier / "stress_results.json"
        result = json.loads(path.read_text())
        result[0]["violations"] = [{"metric": "pipe_freeboard"}]
        self.write_json(path, result)
        with self.assertRaises(AssertionError):
            validate(self.job, 1, "oracle")

    def test_rejects_overriding_reward_json(self):
        self.prepare()
        self.write_json(self.verifier / "reward.json", {"reward": .5})
        with self.assertRaises(AssertionError):
            validate(self.job, 1, "oracle")


if __name__ == "__main__":
    unittest.main()
