# Tecnopolo drainage retrofit

A Terminal-Bench-Science task on rainfall quality control, hydraulic parameter inference, and drainage retrofit design under compound operating conditions.

The task uses the Harbor directory layout. The agent receives the scientific inputs and writes three JSON artifacts. A separate verifier checks the rainfall and network basis, predictive accuracy, lifecycle cost, and hydraulic performance.

## Task files

The task is located at [tasks/engineering-sciences/civil-engineering/tecnopolo-drainage-retrofit](tasks/engineering-sciences/civil-engineering/tecnopolo-drainage-retrofit/).

| File or directory | Purpose |
|---|---|
| [instruction.md](tasks/engineering-sciences/civil-engineering/tecnopolo-drainage-retrofit/instruction.md) | Agent-facing scientific assignment and output contract |
| [task.toml](tasks/engineering-sciences/civil-engineering/tecnopolo-drainage-retrofit/task.toml) | Resources, artifacts, time limits, and verifier configuration |
| `environment/` | Agent image and public scientific inputs |
| `solution/` | Executable reference solution |
| `tests/` | Separate verifier image, pytest checks, and verification fixtures |
| `authoring/` | Provenance, validation records, and reference results |

## Run with Harbor

Install Docker and Harbor, then run these commands from this directory:

```bash
harbor run -p tasks/engineering-sciences/civil-engineering/tecnopolo-drainage-retrofit --agent oracle
harbor run -p tasks/engineering-sciences/civil-engineering/tecnopolo-drainage-retrofit --agent nop
```

Use Harbor to provide the instruction and prepared environment to a solving agent. The task source contains the reference solution and private verification fixtures; it is not the agent workspace.

The declared outputs are `/root/results/calibration.json`, `/root/results/retrofit_design.json`, and `/root/results/design_basis.json`. Verification produces a binary reward and a CTRF test report. No manual investigation handoff is required.

## Validation

Native Windows verification passed all five pytest checks, including 48 independent hydraulic operating cases. The reference lifecycle cost is 1,420,382.17 CU against a 1,450,000 CU budget. Negative controls cover missing artifacts, duplicate JSON keys, incorrect rainfall analysis, excessive cost, poor calibration, and noncompliant hydraulics.

Detailed results are in [authoring/validation.json](tasks/engineering-sciences/civil-engineering/tecnopolo-drainage-retrofit/authoring/validation.json), with the reference engineering note in [authoring/reference_result/design_report.md](tasks/engineering-sciences/civil-engineering/tecnopolo-drainage-retrofit/authoring/reference_result/design_report.md).

Docker image builds, Harbor oracle/nop trials, and fresh agent difficulty trials remain unverified. Native checks do not establish container or artifact-transfer correctness.

Harbor 0.27.0 loads the task successfully, and `harbor lint --json` returns no findings. Twenty selected official runtime and structure checks also pass. These checks exclude publication identity and proposal approval requirements.

## Automated container validation

[GitHub Actions](https://github.com/ZihanZheng2000/tb-science-urban-drainage/actions/workflows/harbor-validation.yml) builds both Docker images and runs the oracle and nop agents on separate Ubuntu runners. It runs on pushes, pull requests, and manual dispatch. No model API key is needed for these two agents.

The workflow requires oracle reward 1 and nop reward 0, consistent CTRF reports, no infrastructure exception, and a recorded separate verifier environment. Oracle evidence must also contain all 48 successful hydraulic cases and the predictive and cost diagnostics. Build logs and trial evidence are retained as workflow artifacts. The result checker has eight unit tests using explicitly synthetic fixtures; those tests are not container validation evidence.

To run the same checks on a Linux host with Docker:

```bash
python3 -m pip install -r requirements-validation.txt
bash scripts/validate_harbor.sh oracle
bash scripts/validate_harbor.sh nop
```

An optional Windows reproduction helper accepts an explicit Python interpreter:

```powershell
.\native_smoke_test.ps1 -Python 'C:\path\to\venv\Scripts\python.exe'
```

The interpreter must provide the pinned scientific dependencies and verifier tooling specified in the Dockerfiles.

## Requirements

- [Terminal-Bench-Science contribution guide, pinned authoring revision](https://github.com/harbor-framework/terminal-bench-science/blob/48c413db15e310527d11863967db9bec5c3085f0/CONTRIBUTING.md)
- [Terminal-Bench-Science implementation rubric](https://github.com/harbor-framework/terminal-bench-science/blob/48c413db15e310527d11863967db9bec5c3085f0/rubrics/task-implementation.toml)
- [Harbor task format](https://harborframework.com/docs/task-format)

The official guide and rubric govern review; this package's validation notes are not a claim of benchmark acceptance. Source attribution and inherited license notices are retained in the task directory.
