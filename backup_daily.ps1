#Requires -Version 5.1
# Runs a full Frappe site backup (database + public/private files) inside
# the running edupro-backend-1 container and copies the result out to
# backups\daily\<yyyy-MM-dd>\ on the host. Intended to be run daily by a
# Windows Scheduled Task (see register_daily_backup_task.ps1) -- not meant
# to be double-clicked interactively, though it's safe to run manually.
#
# Daily backups are NOT committed to git (backups/* is gitignored by
# default -- see docs/13_Backup_Restore.md §13.2/13.5). This script is
# local disk retention only; sync backups\daily\ to separate off-machine
# storage for real disaster-recovery protection.

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ContainerName = "edupro-backend-1"
$SiteName = "edupro.localhost"
$DailyRoot = Join-Path $ProjectRoot "backups\daily"
$LogFile = Join-Path $DailyRoot "backup.log"
$RetentionDays = 30

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

New-Item -ItemType Directory -Force -Path $DailyRoot | Out-Null

try {
    # Confirm the container is actually running before attempting anything --
    # a clear log line here is much easier to diagnose later than a generic
    # docker-exec failure (e.g. Docker Desktop not started that morning).
    $running = docker ps --filter "name=^${ContainerName}$" --format "{{.Names}}" 2>$null
    if ($running -ne $ContainerName) {
        Write-Log "ERROR: container '$ContainerName' is not running -- is Docker Desktop / the edupro stack up? Skipping backup."
        exit 1
    }

    Write-Log "Starting backup for site $SiteName..."
    $backupOutput = docker exec $ContainerName bench --site $SiteName backup --with-files 2>&1
    Write-Log ($backupOutput -join "`n")

    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR: 'bench backup' exited with code $LASTEXITCODE"
        exit 1
    }

    $today = Get-Date -Format "yyyy-MM-dd"
    $destDir = Join-Path $DailyRoot $today
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null

    # Find the 4 files bench just wrote inside the container (newest set,
    # by the shared timestamp prefix) rather than parsing the summary text,
    # which is more robust to any future formatting changes in bench's output.
    $remoteBackupDir = "/home/frappe/frappe-bench/sites/$SiteName/private/backups"
    $latestPrefix = docker exec $ContainerName bash -c "ls -1 $remoteBackupDir | grep -E '\-database\.sql\.gz$' | sort | tail -n 1 | sed 's/-database.sql.gz//'"
    $latestPrefix = $latestPrefix.Trim()

    if (-not $latestPrefix) {
        Write-Log "ERROR: could not determine the backup file prefix -- nothing copied."
        exit 1
    }

    $suffixes = @("database.sql.gz", "files.tar", "private-files.tar", "site_config_backup.json")
    foreach ($suffix in $suffixes) {
        $remoteFile = "${remoteBackupDir}/${latestPrefix}-${suffix}"
        docker cp "${ContainerName}:${remoteFile}" "$destDir/" | Out-Null
    }

    $copied = Get-ChildItem $destDir | Measure-Object
    if ($copied.Count -lt 4) {
        Write-Log "ERROR: expected 4 files in $destDir, found $($copied.Count) -- backup may be incomplete."
        exit 1
    }

    $totalSize = (Get-ChildItem $destDir | Measure-Object -Property Length -Sum).Sum
    Write-Log "Backup complete: $destDir ($([math]::Round($totalSize / 1MB, 2)) MB, $($copied.Count) files)"

    # Retention: drop dated folders older than $RetentionDays so this
    # doesn't grow unbounded on local disk.
    $cutoff = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem $DailyRoot -Directory | Where-Object {
        try {
            $parsed = [DateTime]::ParseExact($_.Name, "yyyy-MM-dd", $null)
            $parsed -lt $cutoff
        } catch {
            $false
        }
    } | ForEach-Object {
        Write-Log "Removing backup older than $RetentionDays days: $($_.FullName)"
        Remove-Item -Recurse -Force $_.FullName
    }

    Write-Log "Done."
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
