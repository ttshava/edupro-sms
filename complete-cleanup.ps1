# Complete Cleanup Script - Remove Everything
Write-Host "🗑️  COMPLETE CLEANUP - REMOVE EVERYTHING" -ForegroundColor Red
Write-Host "===========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  This will remove:"
Write-Host "  - All Docker containers"
Write-Host "  - All Docker images"  
Write-Host "  - All Docker volumes"
Write-Host "  - All frappe_docker files"
Write-Host "  - All site data"
Write-Host ""

$confirm = Read-Host "Type 'YES' to confirm deletion"
if ($confirm -ne "YES") {
    Write-Host "❌ Cleanup cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "🗑️  Starting cleanup..." -ForegroundColor Yellow

# 1. Stop and remove all containers
Write-Host "`n📋 Step 1: Stopping and removing containers..." -ForegroundColor Yellow
docker compose -f "C:\Users\ttsha\Documents\Edupro SMS\frappe_docker\compose.yaml" down -v 2>$null
docker compose -f "C:\Users\ttsha\Documents\Edupro SMS\frappe_docker\compose.override.yaml" down -v 2>$null

# Remove all Frappe/ERPNext containers
docker ps -a --filter "name=*frappe*" -q | ForEach-Object { docker rm -f $_ 2>$null }
docker ps -a --filter "name=*erpnext*" -q | ForEach-Object { docker rm -f $_ 2>$null }
docker ps -a --filter "name=*edupro*" -q | ForEach-Object { docker rm -f $_ 2>$null }

# 2. Remove images
Write-Host "`n📋 Step 2: Removing images..." -ForegroundColor Yellow
$images = @(
    "frappe/erpnext",
    "frappe/frappe",
    "frappe/bench",
    "mariadb",
    "redis",
    "nginx"
)
foreach ($image in $images) {
    docker rmi -f $(docker images -q $image) 2>$null
}

# 3. Remove volumes
Write-Host "`n📋 Step 3: Removing volumes..." -ForegroundColor Yellow
docker volume rm -f $(docker volume ls -q --filter "name=*frappe*") 2>$null
docker volume rm -f $(docker volume ls -q --filter "name=*erpnext*") 2>$null
docker volume rm -f $(docker volume ls -q --filter "name=*edupro*") 2>$null

# 4. Prune everything
Write-Host "`n📋 Step 4: Pruning Docker..." -ForegroundColor Yellow
docker system prune -a -f
docker volume prune -f
docker network prune -f

# 5. Delete frappe_docker folder
Write-Host "`n📋 Step 5: Deleting frappe_docker folder..." -ForegroundColor Yellow
if (Test-Path "C:\Users\ttsha\Documents\Edupro SMS\frappe_docker") {
    Remove-Item -Recurse -Force "C:\Users\ttsha\Documents\Edupro SMS\frappe_docker" -ErrorAction SilentlyContinue
    Write-Host "✅ frappe_docker folder deleted" -ForegroundColor Green
}

# 6. Delete apps and sites folders
Write-Host "`n📋 Step 6: Deleting apps and sites data..." -ForegroundColor Yellow
$folders = @(
    "C:\Users\ttsha\Documents\Edupro SMS\apps",
    "C:\Users\ttsha\Documents\Edupro SMS\sites",
    "C:\Users\ttsha\Documents\Edupro SMS\logs",
    "C:\Users\ttsha\Documents\Edupro SMS\backups"
)
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Remove-Item -Recurse -Force $folder -ErrorAction SilentlyContinue
        Write-Host "✅ $folder deleted" -ForegroundColor Green
    }
}

# 7. Verify cleanup
Write-Host "`n📋 Step 7: Verifying cleanup..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Containers remaining:" -ForegroundColor Cyan
docker ps -a
Write-Host ""
Write-Host "Images remaining:" -ForegroundColor Cyan
docker images
Write-Host ""
Write-Host "Volumes remaining:" -ForegroundColor Cyan
docker volume ls

Write-Host ""
Write-Host "✅ CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📁 Project folder location:" -ForegroundColor White
Write-Host "   C:\Users\ttsha\Documents\Edupro SMS"
Write-Host ""
Write-Host "Ready for fresh installation of Frappe v15 + Education v15!" -ForegroundColor Green