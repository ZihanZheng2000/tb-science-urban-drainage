"""Check real Harbor trial evidence; never infer success from command exit alone."""
from pathlib import Path
import argparse
import json


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate(job_dir, expected_reward, agent):
    assert expected_reward == (1 if agent == "oracle" else 0), "Agent/reward expectation mismatch"
    reward_files = list(job_dir.rglob("verifier/reward.txt"))
    assert len(reward_files) == 1, f"Expected exactly one trial reward, found {len(reward_files)}"
    reward_file = reward_files[0]
    verifier_dir = reward_file.parent
    trial_dir = verifier_dir.parent
    assert not (verifier_dir / "reward.json").exists(), "Only reward.txt should determine the reward"
    reward = float(reward_file.read_text().strip())
    assert reward in (0, 1) and reward == expected_reward, f"Unexpected reward: {reward}"

    trial = load(trial_dir / "result.json")
    assert trial.get("exception_info") is None, trial.get("exception_info")
    assert trial.get("verifier_environment_mode") == "separate", "Separate verification was not recorded"
    assert trial["agent_info"]["name"] == agent, trial["agent_info"]
    rewards = trial["verifier_result"]["rewards"]
    assert rewards == {"reward": expected_reward}, rewards

    report = load(verifier_dir / "ctrf.json")["results"]
    tests, summary = report["tests"], report["summary"]
    assert len(tests) == 5 and summary["tests"] == 5, "Expected all five scientific checks"
    counts = {status: sum(test["status"] == status for test in tests)
              for status in ("passed", "failed", "skipped", "pending", "other")}
    for status, count in counts.items():
        assert summary.get(status, 0) == count, f"Inconsistent CTRF count: {status}"
    assert sum(counts.values()) == len(tests), "Unsupported or missing CTRF test status"
    assert counts["skipped"] == 0 and counts["pending"] == 0 and counts["other"] == 0
    if expected_reward == 1:
        assert counts["passed"] == 5 and counts["failed"] == 0
        operating_cases = load(verifier_dir / "stress_results.json")
        assert len(operating_cases) == 48
        assert len({case["id"] for case in operating_cases}) == 48
        assert all(not case["violations"] for case in operating_cases)
        assert load(verifier_dir / "costs.json")["lifecycle_CU"] <= 1_450_000
        prediction = load(verifier_dir / "prediction.json")
        assert len(prediction["observation_scale_rmse"]) == 12
        assert all(row["rmse_in_noise_sd"] <= 2 for row in prediction["observation_scale_rmse"])
    else:
        assert counts["failed"] > 0, "Nop must fail scientific checks rather than infrastructure"
    return {"agent": agent, "expected_reward": expected_reward, "actual_reward": reward,
            "separate_verifier": True, "trial_exception": None, "ctrf": summary,
            "hydraulic_cases_passed": 48 if expected_reward == 1 else None,
            "trial": str(trial_dir), "passed": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("job_dir", type=Path)
    parser.add_argument("--expected-reward", type=int, choices=(0, 1), required=True)
    parser.add_argument("--agent", choices=("oracle", "nop"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.job_dir, args.expected_reward, args.agent)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
