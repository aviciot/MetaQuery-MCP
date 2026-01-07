# Omni2 Admin Dashboard - Backend Setup and Test Script
# Run this script to set up the backend and verify it works

Write-Host "🚀 Omni2 Admin Dashboard - Backend Setup" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
$backendDir = "c:\Users\acohen.SHIFT4CORP\Desktop\PythonProjects\MCP Performance\omni2-admin\backend"
Set-Location $backendDir

Write-Host "📁 Working directory: $backendDir" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host "   Please review and update DATABASE_URL if needed" -ForegroundColor Yellow
    Write-Host ""
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Run Alembic migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Cyan
alembic upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database migrations completed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to run migrations" -ForegroundColor Red
    Write-Host "   Make sure Omni2 PostgreSQL is running on localhost:5433" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Seed admin user
Write-Host "👤 Seeding admin user..." -ForegroundColor Cyan
python scripts/seed_admin.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Admin user seeded" -ForegroundColor Green
} else {
    Write-Host "⚠️  Admin user may already exist or seeding failed" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Default Admin Credentials:" -ForegroundColor Yellow
Write-Host "   Email:    admin@omni2.local"
Write-Host "   Password: admin123"
Write-Host "   ⚠️  Change this password after first login!"
Write-Host ""
Write-Host "🚀 To start the server:" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload --port 8500"
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "   API:       http://localhost:8500"
Write-Host "   Docs:      http://localhost:8500/docs"
Write-Host "   Health:    http://localhost:8500/health"
Write-Host ""
Write-Host "🧪 Test the auth endpoint:" -ForegroundColor Cyan
Write-Host "   `$body = @{email=`"admin@omni2.local`"; password=`"admin123`"} | ConvertTo-Json" -ForegroundColor White
Write-Host "   Invoke-RestMethod -Uri http://localhost:8500/api/v1/auth/login -Method Post -Body `$body -ContentType `"application/json`"" -ForegroundColor White
Write-Host ""
