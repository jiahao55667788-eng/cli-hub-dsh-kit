#Requires -Version 5.1
<#
.SYNOPSIS
  Install CLI-Hub (CLI-Anything) into an isolated venv and wire it into an agent harness.

.DESCRIPTION
  Clone HKUDS/CLI-Anything, create a private venv, install the `cli-hub` package manager
  from local source (so the registry matches the checkout), install `uv` for public-CLI
  installs, publish a `cli-hub` shim on PATH, and drop the `cli-hub-meta-skill` agent skill
  where DSH / Claude Code / Codex pick it up.

  Everything lands under -Root. Deleting that folder is a complete rollback.

.PARAMETER Root
  Install root. Default: %USERPROFILE%\cli-anything

.PARAMETER SkillDir
  Agent skill directory. Default: %USERPROFILE%\.agents\skills

.PARAMETER ShimDir
  Directory put on PATH for the `cli-hub` shim. Default: %USERPROFILE%\.dsh\bin when it
  exists, otherwise %USERPROFILE%\.local\bin

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\install-cli-hub.ps1
#>
param(
  [string]$Root = (Join-Path $env:USERPROFILE 'cli-anything'),
  [string]$SkillDir = (Join-Path $env:USERPROFILE '.agents\skills'),
  [string]$ShimDir
)

$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "    $msg" -ForegroundColor Green }

if (-not $ShimDir) {
  $dshBin = Join-Path $env:USERPROFILE '.dsh\bin'
  $ShimDir = if (Test-Path $dshBin) { $dshBin } else { Join-Path $env:USERPROFILE '.local\bin' }
}

Step "prerequisites"
foreach ($c in 'git', 'python') {
  if (-not (Get-Command $c -ErrorAction SilentlyContinue)) { throw "$c not found on PATH" }
}
Ok ("git " + (git --version))
Ok ("python " + (python --version 2>&1))

Step "clone CLI-Anything -> $Root"
if (Test-Path (Join-Path $Root 'cli-hub')) {
  Ok 'checkout already present, reusing'
} else {
  New-Item -ItemType Directory -Force -Path (Split-Path $Root -Parent) | Out-Null
  git clone --depth 1 https://github.com/HKUDS/CLI-Anything.git $Root
  if ($LASTEXITCODE -ne 0) { throw 'git clone failed' }
  Ok 'cloned'
}

Step 'create isolated venv'
$venv = Join-Path $Root '.venv'
$py   = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $py)) {
  python -m venv $venv
  if ($LASTEXITCODE -ne 0) { throw 'venv creation failed' }
}
Ok $py

Step 'install cli-hub (editable, local source) + uv'
& (Join-Path $venv 'Scripts\pip.exe') install --upgrade pip --quiet
& (Join-Path $venv 'Scripts\pip.exe') install -e (Join-Path $Root 'cli-hub') --quiet
if ($LASTEXITCODE -ne 0) { throw 'cli-hub install failed' }
& (Join-Path $venv 'Scripts\pip.exe') install --quiet uv
Ok ((& (Join-Path $venv 'Scripts\cli-hub.exe') --version) -join '')

Step "publish shim -> $ShimDir\cli-hub.cmd"
New-Item -ItemType Directory -Force -Path $ShimDir | Out-Null
$exe = Join-Path $venv 'Scripts\cli-hub.exe'
$shim = @(
  '@echo off',
  'setlocal',
  'set "PYTHONUTF8=1"',
  'set "PYTHONIOENCODING=utf-8"',
  ('set "PATH=' + (Join-Path $venv 'Scripts') + ';%PATH%"'),
  ('"' + $exe + '" %*')
)
Set-Content -Path (Join-Path $ShimDir 'cli-hub.cmd') -Value $shim -Encoding ASCII
Ok 'shim written'

Step 'extend user PATH'
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$parts = @()
if ($userPath) { $parts = $userPath.Split(';') | Where-Object { $_ } }
foreach ($p in @($ShimDir, (Join-Path $venv 'Scripts'))) {
  if ($parts -notcontains $p) { $parts += $p; Ok "added $p" }
}
[Environment]::SetEnvironmentVariable('Path', ($parts -join ';'), 'User')

Step "install agent skill -> $SkillDir\cli-hub-meta-skill"
New-Item -ItemType Directory -Force -Path (Join-Path $SkillDir 'cli-hub-meta-skill') | Out-Null
Copy-Item (Join-Path $Root 'cli-hub-meta-skill\SKILL.md') (Join-Path $SkillDir 'cli-hub-meta-skill\SKILL.md') -Force
Ok 'SKILL.md installed'

Step 'verify'
& (Join-Path $Root '.venv\Scripts\cli-hub.exe') list | Select-Object -First 6
Ok 'done'

Write-Host ''
Write-Host 'Next:' -ForegroundColor Yellow
Write-Host '  cli-hub search video'
Write-Host '  cli-hub can "edit a video"'
Write-Host '  cli-hub install mermaid'
Write-Host '  cli-hub matrix install image-design'
Write-Host ''
Write-Host "Rollback: remove $Root, drop those two PATH entries, delete the skill folder." -ForegroundColor DarkGray
