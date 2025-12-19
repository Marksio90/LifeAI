# LifeAI Local Testing Script for Windows
# PowerShell version

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   LifeAI Local Testing Suite        ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

function Print-Header {
    param($message)
    Write-Host ""
    Write-Host "► $message" -ForegroundColor Yellow
    Write-Host ""
}

function Print-Success {
    param($message)
    Write-Host "✓ $message" -ForegroundColor Green
}

function Print-Error {
    param($message)
    Write-Host "✗ $message" -ForegroundColor Red
}

# Check prerequisites
Print-Header "Step 1: Checking Prerequisites"

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Print-Success "Python installed: $pythonVersion"
} else {
    Print-Error "Python 3.11+ is required"
    Print-Error "Download from: https://www.python.org/downloads/"
    exit 1
}

# Check Node
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Print-Success "Node.js installed: $nodeVersion"
} else {
    Print-Error "Node.js 18+ is required"
    Print-Error "Download from: https://nodejs.org/"
    exit 1
}

# Check Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $dockerVersion = docker --version
    Print-Success "Docker installed: $dockerVersion"
} else {
    Print-Error "Docker Desktop is required"
    Print-Error "Download from: https://www.docker.com/products/docker-desktop/"
    exit 1
}

# Check Docker Compose
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    $composeVersion = docker-compose --version
    Print-Success "Docker Compose installed: $composeVersion"
} else {
    Print-Error "Docker Compose is required (included in Docker Desktop)"
    exit 1
}

# Step 2: Environment Setup
Print-Header "Step 2: Checking Environment Files"

if (-not (Test-Path "backend\.env")) {
    Print-Error "Backend .env file not found"
    Write-Host "Creating from .env.example..."
    Copy-Item "backend\.env.example" "backend\.env"
    Print-Success "Created backend\.env"
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit backend\.env and add your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "   Open backend\.env in notepad and change:" -ForegroundColor Yellow
    Write-Host "   OPENAI_API_KEY=sk-your-real-api-key-here" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Press Enter when done, or 'skip' to continue without it"
    if ($response -eq 'skip') {
        Write-Host "⚠️  Continuing without OPENAI_API_KEY - some features won't work" -ForegroundColor Yellow
    }
}

if (-not (Test-Path "frontend\.env.local")) {
    Print-Error "Frontend .env.local file not found"
    Write-Host "Creating from .env.example..."
    Copy-Item "frontend\.env.example" "frontend\.env.local"
    Print-Success "Created frontend\.env.local"
}

# Step 3: Start Infrastructure
Print-Header "Step 3: Starting Infrastructure (PostgreSQL, Redis)"

Write-Host "Starting PostgreSQL and Redis with Docker Compose..."
docker-compose up -d postgres redis

# Wait for services to be ready
Write-Host "Waiting for services to be healthy..."
Start-Sleep -Seconds 10

# Check PostgreSQL
try {
    docker-compose exec -T postgres pg_isready -U lifeai | Out-Null
    Print-Success "PostgreSQL is ready"
} catch {
    Print-Error "PostgreSQL failed to start"
    docker-compose logs postgres
    exit 1
}

# Check Redis
try {
    $redisCheck = docker-compose exec -T redis redis-cli ping
    if ($redisCheck -match "PONG") {
        Print-Success "Redis is ready"
    }
} catch {
    Print-Error "Redis failed to start"
    docker-compose logs redis
    exit 1
}

# Step 4: Backend Setup
Print-Header "Step 4: Backend Setup"

Push-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
    Print-Success "Virtual environment created"
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies (this may take a few minutes)..."
pip install --upgrade pip | Out-Null
pip install -r requirements.txt | Out-Null
Print-Success "Python dependencies installed"

Pop-Location

# Step 5: Database Migrations
Print-Header "Step 5: Running Database Migrations"

Push-Location backend
.\venv\Scripts\Activate.ps1

Write-Host "Running Alembic migrations..."
alembic upgrade head
Print-Success "Database migrations completed"

Pop-Location

# Step 6: Backend Tests
Print-Header "Step 6: Running Backend Tests"

Push-Location backend
.\venv\Scripts\Activate.ps1

Write-Host "Running pytest..."
pytest -v --cov=app --cov-report=term-missing

if ($LASTEXITCODE -eq 0) {
    Print-Success "Backend tests passed!"
} else {
    Print-Error "Backend tests failed!"
    Pop-Location
    exit 1
}

Pop-Location

# Step 7: Frontend Setup
Print-Header "Step 7: Frontend Setup"

Push-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies (this may take a few minutes)..."
    npm install
    Print-Success "Node.js dependencies installed"
} else {
    Print-Success "Node.js dependencies already installed"
}

Pop-Location

# Step 8: Frontend Tests
Print-Header "Step 8: Running Frontend Tests"

Push-Location frontend

Write-Host "Running Jest tests..."
npm test -- --passWithNoTests

if ($LASTEXITCODE -eq 0) {
    Print-Success "Frontend tests passed!"
} else {
    Print-Error "Frontend tests failed!"
    Pop-Location
    exit 1
}

Pop-Location

# Step 9: Start Application
Print-Header "Step 9: Starting Application"

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

Write-Host "Starting backend..."
Push-Location backend
.\venv\Scripts\Activate.ps1

# Start backend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000" -WindowStyle Minimized
Print-Success "Backend started in new window"

Pop-Location

# Wait for backend to be ready
Write-Host "Waiting for backend to be ready..."
$maxAttempts = 30
$attempt = 0
$backendReady = $false

while ($attempt -lt $maxAttempts -and -not $backendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Print-Success "Backend is ready"
        }
    } catch {
        Start-Sleep -Seconds 1
        $attempt++
    }
}

if (-not $backendReady) {
    Print-Error "Backend failed to start within 30 seconds"
    exit 1
}

Write-Host "Starting frontend..."
Push-Location frontend

# Start frontend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Minimized
Print-Success "Frontend started in new window"

Pop-Location

# Wait for frontend to be ready
Write-Host "Waiting for frontend to be ready..."
$attempt = 0
$frontendReady = $false

while ($attempt -lt $maxAttempts -and -not $frontendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $frontendReady = $true
            Print-Success "Frontend is ready"
        }
    } catch {
        Start-Sleep -Seconds 1
        $attempt++
    }
}

# Step 10: Health Checks
Print-Header "Step 10: Running Health Checks"

try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health/" -Method Get
    Print-Success "Backend health check passed"
    $healthResponse | ConvertTo-Json
} catch {
    Print-Error "Backend health check failed"
}

try {
    $readyResponse = Invoke-RestMethod -Uri "http://localhost:8000/health/ready" -Method Get
    Print-Success "Backend readiness check passed"
    $readyResponse | ConvertTo-Json
} catch {
    Print-Error "Backend readiness check failed"
}

# Step 11: Summary
Print-Header "Test Summary"

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║     All Tests Completed! ✓           ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Services Running:" -ForegroundColor Yellow
Write-Host "  • PostgreSQL:  http://localhost:5432"
Write-Host "  • Redis:       http://localhost:6379"
Write-Host "  • Backend API: http://localhost:8000"
Write-Host "  • Frontend:    http://localhost:3000"
Write-Host "  • API Docs:    http://localhost:8000/docs"
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"
Start-Process "http://localhost:8000/docs"
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Yellow
Write-Host "  • Close the PowerShell windows running backend and frontend"
Write-Host "  • Run: docker-compose down"
Write-Host ""
Write-Host "Ready to test at: http://localhost:3000" -ForegroundColor Green
Write-Host ""
