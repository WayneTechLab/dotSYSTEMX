$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$installation = Join-Path $PSScriptRoot 'INSTALLATION.json'
if ((Test-Path -LiteralPath $installation) -or
    ($null -ne (Get-Item -LiteralPath $installation -Force -ErrorAction SilentlyContinue))) {
    # Existing managed state must be validated; never fall back if it is malformed.
    $manager = Join-Path $PSScriptRoot 'manager.py'
    $parameters = @('-I', '-B', $manager, 'run', '--target', $projectRoot, '--') + $args
} else {
    # A reviewed folder-only template can use its local runner without installation.
    $runner = Join-Path $PSScriptRoot 'scripts/systemx.py'
    $parameters = @('-I', '-B', $runner) + $args
}
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 @parameters
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 @parameters
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python @parameters
} else {
    throw 'Install Python 3.9 or newer to use the optional command tools.'
}
exit $LASTEXITCODE
