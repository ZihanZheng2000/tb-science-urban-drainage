#!/usr/bin/env bash
set -euo pipefail

agent="${1:-}"
case "$agent" in
    oracle) expected_reward=1 ;;
    nop) expected_reward=0 ;;
    *) echo "Usage: bash scripts/validate_harbor.sh oracle|nop" >&2; exit 2 ;;
esac

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repository_root"
task="tasks/earth-sciences/geosciences/tecnopolo-drainage-retrofit"
evidence="$repository_root/validation/$agent"
mkdir -p "$evidence"
export HARBOR_TELEMETRY=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1

python3 -c "from importlib.metadata import version; assert version('harbor') == '0.27.0'"
harbor --version > "$evidence/harbor-version.txt"
docker version > "$evidence/docker-version.txt" 2>&1
docker info > "$evidence/docker-info.txt" 2>&1
harbor lint --json "$task" > "$evidence/lint.json"

# Explicit builds expose dependency and platform errors before the trial starts.
# Harbor subsequently builds its own images using Docker's cached layers.
docker build --progress=plain -t "tb-science-swmm-agent:$agent" "$task/environment" \
    2>&1 | tee "$evidence/agent-build.log"
docker build --progress=plain -t "tb-science-swmm-verifier:$agent" "$task/tests" \
    2>&1 | tee "$evidence/verifier-build.log"

harbor run -p "$task" -a "$agent" -e docker -r 0 -n 1 -k 1 \
    -o "$evidence/jobs" --job-name "$agent" \
    2>&1 | tee "$evidence/harbor-run.log"

# A successful Harbor command alone does not establish a successful trial.
# Require the expected reward, a consistent CTRF report, no trial exception,
# and an explicitly recorded separate verifier environment.
python3 scripts/check_harbor_results.py "$evidence/jobs/$agent" \
    --expected-reward "$expected_reward" --agent "$agent" \
    --output "$evidence/validation-summary.json"
