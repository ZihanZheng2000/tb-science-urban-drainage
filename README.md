# Tecnopolo drainage retrofit

An interview benchmark in the Harbor task format, focused on urban stormwater and environmental hydrology: rainfall quality control, hydraulic parameter inference, and drainage retrofit design under compound operating conditions.

The task uses the Harbor directory layout. The agent receives the scientific inputs and writes three JSON artifacts. A separate verifier checks the rainfall and network basis, predictive accuracy, lifecycle cost, and hydraulic performance.

## Task files

The task is located at [tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit](tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit/).

| File or directory | Purpose |
|---|---|
| [instruction.md](tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit/instruction.md) | Agent-facing scientific assignment and output contract |
| [task.toml](tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit/task.toml) | Resources, artifacts, time limits, and verifier configuration |
| `environment/` | Agent image and public scientific inputs |
| `solution/` | Executable reference solution |
| `tests/` | Separate verifier image, pytest checks, and verification fixtures |
| `authoring/` | Provenance, validation records, and reference results |

## Run with Harbor

Install Docker and Harbor, then run these commands from this directory:

```bash
harbor run -p tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit --agent oracle
harbor run -p tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit --agent nop
```

Use Harbor to provide the instruction and prepared environment to a solving agent. The task source contains the reference solution and private verification fixtures; it is not the agent workspace.

The declared outputs are `/root/results/calibration.json`, `/root/results/retrofit_design.json`, and `/root/results/design_basis.json`. Verification produces a binary reward and a CTRF test report. No manual investigation handoff is required.

## Validation

Native Windows verification passed all five pytest checks, including 48 independent hydraulic operating cases. The reference lifecycle cost is 1,420,382.17 CU. Cost is minimized among scientifically and hydraulically feasible designs; the agent is not given a budget or a numerical acceptance target. Negative controls cover missing artifacts, duplicate JSON keys, incorrect rainfall analysis, excessive cost, poor calibration, and noncompliant hydraulics.

Detailed results are in [authoring/validation.json](tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit/authoring/validation.json), with the reference engineering note in [authoring/reference_result/design_report.md](tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit/authoring/reference_result/design_report.md).

The feasibility-first cost contract passed Docker builds and Harbor end-to-end validation on Ubuntu 24.04: **oracle reward 1**, **nop reward 0**, and **48/48 hydraulic cases**. Both trials recorded separate verification with no infrastructure exception. See the [successful workflow run](https://github.com/ZihanZheng2000/tb-science-urban-drainage/actions/runs/45955858993) and [container validation record](tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit/authoring/container_validation.json). The validated runtime source is commit `178d151ac7cd`. Current-version model difficulty has not been measured; the prior-variant result is summarized below.

Harbor 0.27.0 loads the task successfully, and `harbor lint --json` returns no findings. Twenty selected official runtime and structure checks also pass. These checks exclude publication identity and proposal approval requirements.

## Automated container validation

[GitHub Actions](https://github.com/ZihanZheng2000/tb-science-urban-drainage/actions/workflows/harbor-validation.yml) builds both Docker images and runs the oracle and nop agents on separate Ubuntu runners. It runs on pushes, pull requests, and manual dispatch. No model API key is needed for these two agents.

The workflow requires oracle reward 1 and nop reward 0, consistent CTRF reports, no infrastructure exception, and a recorded separate verifier environment. Oracle evidence must also contain all 48 successful hydraulic cases and the predictive and cost diagnostics. Build logs and trial evidence are retained as workflow artifacts. The result checker and feasibility-first economics have unit tests using explicitly synthetic fixtures; those tests are not container validation evidence.

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

## Prior agent trial

A previous version of the same drainage scenario was tested with Claude Code, identified by the user as **Claude Opus 5.5**. The design **met the hydraulic engineering requirements, passing 48/48 cases**, with prediction P=0.998268. Its lifecycle cost was **1,475,426.83 CU**, compared with **1,420,382.17 CU** for the reference design: a feasible engineering solution with further scope to reduce cost.

That version used a two-phase workflow and different scoring. This is a prior-variant reference, not a current-version failure or a measured frontier-model pass rate. The saved grader record does not include an exact model ID; the Opus 5.5 label is user-reported. See [the compact trial record](tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit/authoring/evidence/claude_opus_5_5_prior_variant.json).

## Requirements

- [Terminal-Bench-Science contribution guide, pinned authoring revision](https://github.com/harbor-framework/terminal-bench-science/blob/48c413db15e310527d11863967db9bec5c3085f0/CONTRIBUTING.md)
- [Terminal-Bench-Science implementation rubric](https://github.com/harbor-framework/terminal-bench-science/blob/48c413db15e310527d11863967db9bec5c3085f0/rubrics/task-implementation.toml)
- [Harbor task format](https://harborframework.com/docs/task-format)

This repository is an interview deliverable, not an official benchmark submission. Author identity metadata and official proposal/review steps are intentionally outside its scope; passing Harbor runtime validation does not mean passing all official publication checks. Source attribution and inherited license notices are retained in the task directory.
