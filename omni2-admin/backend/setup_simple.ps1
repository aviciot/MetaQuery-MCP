# Omni2 Admin Dashboard - Backend Setup Script
Write-Host "Omni2 Admin Dashboard - Backend Setup" -ForegroundColor Cyan
Write-Host ""

$backendDir = "c:\Users\acohen.SHIFT4CORP\Desktop\PythonProjects\MCP Performance\omni2-admin\backend"
Set-Location $backendDir

Write-Host "Working directory: $backendDir" -ForegroundColor Green
Write-Host ""

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "[1/5] Copying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "      Created .env file" -ForegroundColor Green
    Write-Host ""
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "[2/5] Creating virtual environment with Python 3.12..." -ForegroundColor Cyan
    py -3.12 -m venv venv
    Write-Host "      Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate and install dependencies
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip -q
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "      Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "      Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Run migrations
Write-Host "[4/5] Running database migrations..." -ForegroundColor Cyan
alembic upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "      Database migrations completed" -ForegroundColor Green
} else {
    Write-Host "      Failed - Make sure Omni2 PostgreSQL is running!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Seed admin
Write-Host "[5/5] Seeding admin user..." -ForegroundColor Cyan
python scripts/seed_admin.py
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Default Admin Credentials:" -ForegroundColor Yellow
Write-Host "  Email:    admin@omni2.local"
Write-Host "  Password: admin123"
Write-Host ""
Write-Host "To start the server:" -ForegroundColor Cyan
Write-Host "  uvicorn app.main:app --reload --port 8500"
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  API:    http://localhost:8500"
Write-Host "  Docs:   http://localhost:8500/docs"
Write-Host "  Health: http://localhost:8500/health"
Write-Host ""
