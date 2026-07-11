#Requires -Version 5.1
# Registers a Windows Scheduled Task that runs backup_daily.ps1 every day
# at 02:00, taking a full Frappe site backup (database + files) into
# backups\daily\<yyyy-MM-dd>\ on this machine. Double-click this file (or
# right-click > Run with PowerShell) -- it re-launches itself elevated if
# needed, so you'll see one UAC prompt. Re-run any time to update the
# schedule; it removes and recreates the task, so it's safe to run again.

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

Write-Host "Running elevated. Registering scheduled task..."

$TaskName = "Edupro SMS Daily Backup"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackupScript = Join-Path $ScriptDir "backup_daily.ps1"

if (-not (Test-Path $BackupScript)) {
    Write-Host "ERROR: backup_daily.ps1 not found next to this script at $BackupScript" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Task already exists -- removing old one first."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$BackupScript`""

$trigger = New-ScheduledTaskTrigger -Daily -At "02:00"

# Run only when the current user is logged on -- Docker Desktop runs in
# the user's session on this machine, not as a system service, so a
# backup attempted while nobody's logged in would just fail anyway.
# StartWhenAvailable catches up on the next logon if the machine was off
# or asleep at 02:00.
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings `
    -Description "Daily full backup (database + files) of the Edupro SMS Frappe site into backups\daily\. See docs\13_Backup_Restore.md." `
    | Out-Null

Write-Host ""
Write-Host "SUCCESS. '$TaskName' scheduled for 02:00 daily." -ForegroundColor Green
Write-Host "Backups land in: $ScriptDir\backups\daily\<yyyy-MM-dd>\" -ForegroundColor Green
Write-Host "Log file: $ScriptDir\backups\daily\backup.log" -ForegroundColor Green
Write-Host ""
Write-Host "To test it right now: Start-ScheduledTask -TaskName `"$TaskName`"" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close"
