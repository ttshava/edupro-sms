#Requires -Version 5.1
# Adds the "Edupro SMS LAN Access" inbound firewall rule (TCP 8080, all
# network profiles -- this machine's Ethernet adapter is currently
# classified "Public" by Windows, not "Private", so the rule must cover
# both to actually work). Double-click this file (or right-click > Run
# with PowerShell) -- it re-launches itself elevated if needed, so you'll
# see one UAC prompt. Click "Yes" on that prompt; the rest is automatic.

$ErrorActionPreference = "Stop"

function Test-IsAdmin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-IsAdmin)) {
    Write-Host "Not elevated -- relaunching as Administrator (approve the UAC prompt)..."
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process powershell.exe -Verb RunAs -ArgumentList @(
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$scriptPath`""
    )
    exit
}

Write-Host "Running elevated. Configuring firewall rule..."

$svc = Get-Service -Name MpsSvc -ErrorAction SilentlyContinue
if (-not $svc -or $svc.Status -ne "Running") {
    Write-Host "ERROR: Windows Defender Firewall service (MpsSvc) is not running." -ForegroundColor Red
    Write-Host "Status: $($svc.Status), StartType: $($svc.StartType)" -ForegroundColor Red
    Write-Host "This machine likely has a policy blocking firewall changes. Contact your IT admin." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

$existing = Get-NetFirewallRule -DisplayName "Edupro SMS LAN Access" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Rule already exists -- removing old one first."
    Remove-NetFirewallRule -DisplayName "Edupro SMS LAN Access" -Confirm:$false
}

New-NetFirewallRule `
    -DisplayName "Edupro SMS LAN Access" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8080 `
    -Action Allow `
    -Profile Any `
    -Description "Allows LAN devices (Ethernet + Wi-Fi) to reach the Edupro SMS Docker frontend on port 8080"

Write-Host ""
Write-Host "SUCCESS. Firewall rule added (all network profiles)." -ForegroundColor Green
Write-Host "Other devices on this network -- wired or Wi-Fi -- can now reach:" -ForegroundColor Green
Write-Host "  http://192.168.1.100:8080/login" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to close"
