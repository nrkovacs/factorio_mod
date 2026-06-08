$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$info = Get-Content -LiteralPath (Join-Path $repoRoot "info.json") -Raw | ConvertFrom-Json
$packageName = "$($info.name)_$($info.version)"
$dist = Join-Path $repoRoot "dist"
$stagingRoot = Join-Path $dist "_staging"
$packageRoot = Join-Path $stagingRoot $packageName
$zipPath = Join-Path $dist "$packageName.zip"

$paths = @(
  "control.lua",
  "data.lua",
  "info.json",
  "thumbnail.png",
  "README.md",
  "docs",
  "graphics",
  "locale",
  "prototypes",
  "wiki"
)

if (Test-Path $stagingRoot) {
  Remove-Item -LiteralPath $stagingRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $packageRoot | Out-Null

foreach ($path in $paths) {
  $source = Join-Path $repoRoot $path
  $destination = Join-Path $packageRoot $path
  if (Test-Path $source -PathType Container) {
    Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force
  } else {
    Copy-Item -LiteralPath $source -Destination $destination -Force
  }
}

if (Test-Path $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -Path $packageRoot -DestinationPath $zipPath -Force
Remove-Item -LiteralPath $stagingRoot -Recurse -Force
Write-Output $zipPath
