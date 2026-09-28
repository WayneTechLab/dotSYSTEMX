# Run from a reviewed checkout or extracted release. No admin or policy changes.
$ErrorActionPreference = 'Stop'
$runner = Join-Path $PSScriptRoot 'manager.py'
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -B $runner install @args
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 -B $runner install @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python -B $runner install @args
} else {
    throw 'Install Python 3.9 or newer, then run this installer again.'
}
exit $LASTEXITCODE
