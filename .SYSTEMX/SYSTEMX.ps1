$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$manager = Join-Path $PSScriptRoot 'manager.py'
$parameters = @('-B', $manager, 'run', '--target', $projectRoot, '--') + $args
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
