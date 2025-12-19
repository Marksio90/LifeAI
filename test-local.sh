#!/bin/bash
# LifeAI Local Testing Script
# This script sets up and tests the entire platform locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   LifeAI Local Testing Suite        ║${NC}"
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo ""

# Function to print section headers
print_header() {
    echo -e "\n${YELLOW}► $1${NC}\n"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
print_header "Step 1: Checking Prerequisites"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python installed: $PYTHON_VERSION"
else
    print_error "Python 3.11+ is required"
    exit 1
fi

# Check Node
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"
else
    print_error "Node.js 18+ is required"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker installed: $DOCKER_VERSION"
else
    print_error "Docker is required"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_success "Docker Compose installed: $COMPOSE_VERSION"
else
    print_error "Docker Compose is required"
    exit 1
fi

# Step 2: Environment Setup
print_header "Step 2: Setting Up Environment"

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    print_error "Backend .env file not found"
    echo "Creating from .env.example..."
    cp backend/.env.example backend/.env
    print_success "Created backend/.env - Please edit with your API keys"
    echo -e "${YELLOW}Required: Add your OPENAI_API_KEY to backend/.env${NC}"
    read -p "Press Enter when done..."
fi

if [ ! -f "frontend/.env.local" ]; then
    print_error "Frontend .env.local file not found"
    echo "Creating from .env.example..."
    cp frontend/.env.example frontend/.env.local
    print_success "Created frontend/.env.local"
fi

# Step 3: Backend Setup
print_header "Step 3: Backend Setup"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_success "Python dependencies installed"

cd ..

# Step 4: Frontend Setup
print_header "Step 4: Frontend Setup"

cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install > /dev/null 2>&1
    print_success "Node.js dependencies installed"
else
    print_success "Node.js dependencies already installed"
fi

cd ..

# Step 5: Start Infrastructure
print_header "Step 5: Starting Infrastructure (PostgreSQL, Redis)"

echo "Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "Waiting for services to be healthy..."
sleep 5

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U lifeai > /dev/null 2>&1; then
    print_success "PostgreSQL is ready"
else
    print_error "PostgreSQL failed to start"
    docker-compose logs postgres
    exit 1
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is ready"
else
    print_error "Redis failed to start"
    docker-compose logs redis
    exit 1
fi

# Step 6: Database Migrations
print_header "Step 6: Running Database Migrations"

cd backend
source venv/bin/activate

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head
print_success "Database migrations completed"

cd ..

# Step 7: Backend Tests
print_header "Step 7: Running Backend Tests"

cd backend
source venv/bin/activate

echo "Running pytest..."
pytest -v --cov=app --cov-report=term-missing

if [ $? -eq 0 ]; then
    print_success "Backend tests passed!"
else
    print_error "Backend tests failed!"
    exit 1
fi

cd ..

# Step 8: Frontend Tests
print_header "Step 8: Running Frontend Tests"

cd frontend

echo "Running Jest tests..."
npm test -- --passWithNoTests

if [ $? -eq 0 ]; then
    print_success "Frontend tests passed!"
else
    print_error "Frontend tests failed!"
    exit 1
fi

cd ..

# Step 9: Start Application
print_header "Step 9: Starting Application"

echo "Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
print_success "Backend started (PID: $BACKEND_PID)"
cd ..

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
        print_success "Backend is ready"
        break
    fi
    sleep 1
done

echo "Starting frontend..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
print_success "Frontend started (PID: $FRONTEND_PID)"
cd ..

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is ready"
        break
    fi
    sleep 1
done

# Step 10: Health Checks
print_header "Step 10: Running Health Checks"

# Backend health
BACKEND_HEALTH=$(curl -s http://localhost:8000/health/)
if [ $? -eq 0 ]; then
    print_success "Backend health check passed"
    echo "$BACKEND_HEALTH" | python3 -m json.tool
else
    print_error "Backend health check failed"
fi

# Backend readiness
BACKEND_READY=$(curl -s http://localhost:8000/health/ready)
if [ $? -eq 0 ]; then
    print_success "Backend readiness check passed"
    echo "$BACKEND_READY" | python3 -m json.tool
else
    print_error "Backend readiness check failed"
fi

# Frontend health
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend health check passed"
else
    print_error "Frontend health check failed"
fi

# Step 11: API Tests
print_header "Step 11: Testing API Endpoints"

# Test registration
echo "Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
    print_success "User registration successful"
    ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
else
    echo "Registration response: $REGISTER_RESPONSE"
    # User might already exist, try login
    echo "Trying login instead..."
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
      -H "Content-Type: application/json" \
      -d '{
        "email": "test@example.com",
        "password": "TestPassword123!"
      }')

    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        print_success "User login successful"
        ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    else
        print_error "Authentication failed"
        ACCESS_TOKEN=""
    fi
fi

# Test authenticated endpoint
if [ ! -z "$ACCESS_TOKEN" ]; then
    echo "Testing authenticated endpoint..."
    ME_RESPONSE=$(curl -s http://localhost:8000/auth/me \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    if echo "$ME_RESPONSE" | grep -q "email"; then
        print_success "Authenticated endpoint working"
        echo "$ME_RESPONSE" | python3 -m json.tool
    else
        print_error "Authenticated endpoint failed"
    fi
fi

# Step 12: Summary
print_header "Test Summary"

echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     All Tests Completed! ✓           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Services Running:${NC}"
echo "  • PostgreSQL:  http://localhost:5432"
echo "  • Redis:       http://localhost:6379"
echo "  • Backend API: http://localhost:8000"
echo "  • Frontend:    http://localhost:3000"
echo "  • API Docs:    http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "  • Backend:  tail -f logs/backend.log"
echo "  • Frontend: tail -f logs/frontend.log"
echo ""
echo -e "${YELLOW}To stop services:${NC}"
echo "  • Kill processes: kill $BACKEND_PID $FRONTEND_PID"
echo "  • Stop infrastructure: docker-compose down"
echo ""
echo -e "${GREEN}Ready to test at: http://localhost:3000${NC}"
echo ""

# Save PIDs for cleanup
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
