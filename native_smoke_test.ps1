param(
    [Parameter(Mandatory = $true)]
    [string]$Python
)
$ErrorActionPreference = 'Stop'
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
$taskDirectory = Join-Path $PSScriptRoot 'tasks\engineering-sciences\civil-engineering\tecnopolo-drainage-retrofit'
$runDirectory = Join-Path $PSScriptRoot ('author_materials\native_smoke_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
$answerDirectory = Join-Path $runDirectory 'artifacts'
$verifierDirectory = Join-Path $runDirectory 'verifier'
New-Item -ItemType Directory -Path $answerDirectory, $verifierDirectory -Force | Out-Null
& $Python -c "from importlib.metadata import version; assert version('pytest') == '8.4.1'; assert version('pytest-json-ctrf') == '0.3.5'"
if ($LASTEXITCODE -ne 0) {
    throw 'Install pytest==8.4.1 and pytest-json-ctrf==0.3.5 into the selected Python environment first.'
}
& $Python (Join-Path $taskDirectory 'solution\solve.py') --project (Join-Path $taskDirectory 'environment\input') --output $answerDirectory --work (Join-Path $runDirectory 'work') --jobs 2
if ($LASTEXITCODE -ne 0) { throw 'Native reference solution failed.' }
Set-Content -LiteralPath (Join-Path $verifierDirectory 'reward.txt') -Value '0' -Encoding ascii
& $Python -m pytest (Join-Path $taskDirectory 'tests\test_outputs.py') --submission $answerDirectory --diagnostics $verifierDirectory --ctrf (Join-Path $verifierDirectory 'ctrf.json') -p no:cacheprovider -q
if ($LASTEXITCODE -ne 0) { throw 'Native verifier failed; reward remains 0.' }
Set-Content -LiteralPath (Join-Path $verifierDirectory 'reward.txt') -Value '1' -Encoding ascii
Write-Output "Native checks passed. Results: $runDirectory"
Write-Output 'This native check does not execute Docker builds or Harbor artifact isolation.'
