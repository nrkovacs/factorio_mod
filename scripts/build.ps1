$ErrorActionPreference = "Stop"

# Use the same portable ZIP builder on Windows, macOS, Linux, and CI.
# Windows Compress-Archive can create backslash entries that Linux Factorio
# does not recognize as directories.
if (Get-Command python -ErrorAction SilentlyContinue) {
  & python (Join-Path $PSScriptRoot "build.py")
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3 (Join-Path $PSScriptRoot "build.py")
} else {
  throw "Python 3 is required. Install it, then run python scripts/build.py."
}
if ($LASTEXITCODE -ne 0) {
  throw "Mod packaging failed (exit code $LASTEXITCODE)."
}
