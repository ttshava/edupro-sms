# Fresh Installation - Frappe v15 + Education v15
Write-Host "🚀 FRESH INSTALLATION - Frappe v15 + Education v15" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
cd "C:\Users\ttsha\Documents\Edupro SMS"

# 1. Clone frappe_docker
Write-Host "📋 Step 1: Cloning frappe_docker..." -ForegroundColor Yellow
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker

# 2. Create .env file
Write-Host "`n📋 Step 2: Creating .env file..." -ForegroundColor Yellow
@"
# Database Configuration
DB_PASSWORD=root_password_edupro_2025

# Site Configuration
SITE_NAME=edupro.localhost
ADMIN_PASSWORD=admin_edupro_2025

# Development Mode
BENCH_DEVELOPER_MODE=1
"@ | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✅ .env created" -ForegroundColor Green

# 3. Create apps.json with version-15 apps
Write-Host "`n📋 Step 3: Creating apps.json..." -ForegroundColor Yellow
@'
[
    {
        "url": "https://github.com/frappe/frappe",
        "branch": "version-15"
    },
    {
        "url": "https://github.com/frappe/erpnext",
        "branch": "version-15"
    },
    {
        "url": "https://github.com/frappe/payments",
        "branch": "version-15"
    },
    {
        "url": "https://github.com/frappe/education",
        "branch": "version-15"
    }
]
'@ | Out-File -FilePath "apps.json" -Encoding UTF8
Write-Host "✅ apps.json created with version-15 apps" -ForegroundColor Green

# 4. Create compose.override.yaml
Write-Host "`n📋 Step 4: Creating compose.override.yaml..." -ForegroundColor Yellow
@'
services:
  backend:
    environment:
      - BENCH_DEVELOPER_MODE=1
    volumes:
      - ../apps:/home/frappe/frappe-bench/apps
      - ../sites:/home/frappe/frappe-bench/sites
      - ../logs:/home/frappe/frappe-bench/logs
    ports:
      - "8000:8000"
      - "9000:9000"

  frontend:
    environment:
      - NODE_ENV=development
    ports:
      - "8080:8080"

  websocket:
    ports:
      - "9000:9000"

volumes:
  apps:
  sites:
'@ | Out-File -FilePath "compose.override.yaml" -Encoding UTF8
Write-Host "✅ compose.override.yaml created" -ForegroundColor Green

# 5. Start containers
Write-Host "`n📋 Step 5: Starting containers..." -ForegroundColor Yellow
Write-Host "⏳ This will take 5-10 minutes to download images..." -ForegroundColor Yellow
docker compose -f compose.yaml -f compose.override.yaml up -d

# 6. Wait for initialization
Write-Host "`n⏳ Waiting for containers to initialize (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# 7. Create site with v15
Write-Host "`n📋 Step 6: Creating site with Frappe v15..." -ForegroundColor Yellow
docker compose exec backend bench new-site edupro.localhost `
    --admin-password admin_edupro_2025 `
    --db-password root_password_edupro_2025

# 8. Install apps in correct order (CRITICAL)
Write-Host "`n📋 Step 7: Installing apps (ERPNext v15 + Education v15)..." -ForegroundColor Yellow

Write-Host "Installing ERPNext v15..." -ForegroundColor Cyan
docker compose exec backend bench --site edupro.localhost install-app erpnext

Write-Host "Installing Payments..." -ForegroundColor Cyan
docker compose exec backend bench --site edupro.localhost install-app payments

Write-Host "Installing Education v15..." -ForegroundColor Cyan
docker compose exec backend bench --site edupro.localhost install-app education

# 9. Verify installation
Write-Host "`n📋 Step 8: Verifying installation..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Installed apps:" -ForegroundColor Cyan
docker compose exec backend bench --site edupro.localhost list-apps

# 10. Enable developer mode
Write-Host "`n📋 Step 9: Enabling developer mode..." -ForegroundColor Yellow
docker compose exec backend bench --site edupro.localhost set-config developer_mode 1
docker compose exec backend bench --site edupro.localhost clear-cache

Write-Host ""
Write-Host "✅ INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Access your site at: http://localhost:8000" -ForegroundColor White
Write-Host "👤 Username: Administrator" -ForegroundColor White
Write-Host "🔑 Password: admin_edupro_2025" -ForegroundColor White
Write-Host ""
Write-Host "📚 Installed Apps:" -ForegroundColor Yellow
Write-Host "  ✅ Frappe Framework v15" -ForegroundColor Green
Write-Host "  ✅ ERPNext v15" -ForegroundColor Green
Write-Host "  ✅ Payments" -ForegroundColor Green
Write-Host "  ✅ Education v15" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Login to your site" -ForegroundColor White
Write-Host "  2. Access Education module from the workspace" -ForegroundColor White
Write-Host "  3. Start creating Programs, Courses, and Students" -ForegroundColor White
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan

# Open browser
Start-Process "http://localhost:8000"