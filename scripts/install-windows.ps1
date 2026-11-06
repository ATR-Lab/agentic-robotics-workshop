<#
Install what the workshop lab needs on Windows 10 or 11: Python 3, Git and Docker Engine, then pull the station image.

Docker Engine only runs on Linux, so by default this installs WSL 2 with Ubuntu 24.04 and runs scripts/install.sh
inside it: Docker's own repository and the latest docker-ce, docker-ce-cli, containerd.io, docker-buildx-plugin and
docker-compose-plugin. You then run lab steps 03 and 04 from the Ubuntu terminal (all six steps work there).
-DockerDesktop installs Docker Desktop instead, for running every step from Git Bash or PowerShell.

Usage, in PowerShell (not as administrator; Windows asks for permission when a step needs it):
  powershell -ExecutionPolicy Bypass -File scripts\install-windows.ps1 [-DockerDesktop] [-NoPull] [-Distro Ubuntu-24.04]
Before you have the folder:
  irm https://raw.githubusercontent.com/ATR-Lab/agentic-robotics-workshop/main/scripts/install-windows.ps1 -OutFile install-windows.ps1
  powershell -ExecutionPolicy Bypass -File .\install-windows.ps1

Needs winget (App Installer) and hardware virtualization turned on. Safe to run again: it skips what is installed.
Running winget accepts the Python, Git and Docker Desktop package agreements on your behalf.
#>
param(
    [switch]$DockerDesktop,
    [switch]$NoPull,
    [string]$Distro = 'Ubuntu-24.04'
)
$ErrorActionPreference = 'Stop'
$Image = 'ghcr.io/atr-lab/agentic-workshop-station:2026.11'
$RawScript = 'https://raw.githubusercontent.com/ATR-Lab/agentic-robotics-workshop/main/scripts/install.sh'
$env:WSL_UTF8 = '1'   # wsl.exe otherwise prints UTF-16

function Say($text) { Write-Host "`n== $text" -ForegroundColor Cyan }
function Fail($text) { Write-Host "FAIL $text" -ForegroundColor Red; exit 1 }
function Run($exe, [string[]]$arguments) {
    Write-Host ('$ ' + $exe + ' ' + ($arguments -join ' '))
    & $exe @arguments
    if ($LASTEXITCODE -ne 0) { Fail "$exe exited with $LASTEXITCODE" }
}
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                [Environment]::GetEnvironmentVariable('Path', 'User')
}
function Test-Python {
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) { return $false }
    & py -3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>$null
    return ($LASTEXITCODE -eq 0)
}
function Winget-Install($id) {
    Run 'winget' @('install', '-e', '--id', $id, '--accept-source-agreements', '--accept-package-agreements')
    Refresh-Path
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Fail 'winget is missing. Install "App Installer" from the Microsoft Store, open a new PowerShell and run this again.'
}

Say 'Python 3 and Git'
if (Test-Python) { Write-Host "Already installed: $(& py -3 --version)" } else { Winget-Install 'Python.Python.3.13' }
if (Get-Command git -ErrorAction SilentlyContinue) { Write-Host "Already installed: $(& git --version)" } else { Winget-Install 'Git.Git' }

Say 'WSL 2'
& wsl.exe --status *> $null
if ($LASTEXITCODE -ne 0) {
    Run 'wsl.exe' @('--install', '--no-distribution')
    Write-Host "`nWSL is installed. Restart Windows, then run this script again." -ForegroundColor Yellow
    exit 0
}
& wsl.exe --set-default-version 2 *> $null

if ($DockerDesktop) {
    Say 'Docker Desktop'
    if (Test-Path "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe") {
        Write-Host 'Already installed.'
    } else {
        Winget-Install 'Docker.DockerDesktop'
    }
    Refresh-Path
    & docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nStart Docker Desktop from the Start menu, accept its first-run screens, give it at least 4 GB of memory"
        Write-Host '(Settings > Resources), then run this script again to pull the image. You may need to sign out and back in first.'
        exit 0
    }
    if (-not $NoPull) { Say 'Station image (about 1.2 GB)'; Run 'docker' @('pull', $Image) }
    Say 'Done'
    Write-Host 'Next, in Git Bash in the workshop folder:  bash lab/00-check.sh   (PowerShell:  py -3 lab\lab.py 00)'
    Write-Host 'No workshop folder yet:  git clone https://github.com/ATR-Lab/agentic-robotics-workshop'
    exit 0
}

Say "Ubuntu in WSL ($Distro)"
$installed = @(& wsl.exe --list --quiet 2>$null | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if ($installed -notcontains $Distro) {
    Write-Host 'When Ubuntu asks, choose a user name and password (you need the password in a moment).'
    Write-Host 'If it then shows an Ubuntu prompt, type  exit  to come back here.' -ForegroundColor Yellow
    Write-Host "`$ wsl.exe --install -d $Distro"
    & wsl.exe --install -d $Distro
    $installed = @(& wsl.exe --list --quiet 2>$null | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($installed -notcontains $Distro) {
        Write-Host "`n$Distro is not ready yet. Restart Windows if asked, open $Distro once from the Start menu to create your user, then run this script again." -ForegroundColor Yellow
        exit 0
    }
}
$version = (& wsl.exe --list --verbose | Where-Object { $_ -match "\s$([regex]::Escape($Distro))\s" }) -replace '.*\s(\d)\s*$', '$1'
if ($version -eq '1') { Run 'wsl.exe' @('--set-version', $Distro, '2') }

# Docker Engine starts as a systemd service; current Ubuntu images turn systemd on, older ones may not.
& wsl.exe -d $Distro -- test -d /run/systemd/system
if ($LASTEXITCODE -ne 0) {
    Run 'wsl.exe' @('-d', $Distro, '-u', 'root', '--', 'sh', '-c', "printf '[boot]\nsystemd=true\n' >> /etc/wsl.conf")
    Run 'wsl.exe' @('--terminate', $Distro)
}

Say 'Docker Engine inside Ubuntu (asks for your Ubuntu password)'
$local = Join-Path $PSScriptRoot 'install.sh'
$extra = @()
if ($NoPull) { $extra = @('--no-pull') }
if ($PSScriptRoot -and (Test-Path $local)) {
    $linuxPath = (& wsl.exe -d $Distro -- wslpath -a ($local -replace '\\', '/')).Trim()
    Run 'wsl.exe' (@('-d', $Distro, '--', 'bash', $linuxPath) + $extra)
} else {
    Run 'wsl.exe' (@('-d', $Distro, '--', 'bash', '-c', "curl -fsSL $RawScript | bash -s -- $($extra -join ' ')"))
}
# A fresh start of the distro makes the new docker group membership take effect.
Run 'wsl.exe' @('--terminate', $Distro)

Say 'Done'
Write-Host "Open $Distro from the Start menu and run the lab there, in your Ubuntu home folder (not /mnt/c):"
Write-Host '  git clone https://github.com/ATR-Lab/agentic-robotics-workshop'
Write-Host '  cd agentic-robotics-workshop'
Write-Host '  bash lab/00-check.sh'
