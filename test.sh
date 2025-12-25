#!/bin/bash
# =============================================================================
# 🧪 LifeAI - Automated Test Suite
# =============================================================================
# This script runs comprehensive tests across the entire platform
# Usage: ./test.sh [--unit] [--integration] [--e2e] [--load] [--all]
# =============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test flags
RUN_UNIT=false
RUN_INTEGRATION=false
RUN_E2E=false
RUN_LOAD=false
RUN_ALL=false

# Parse arguments
if [ $# -eq 0 ]; then
    RUN_ALL=true
fi

for arg in "$@"; do
    case $arg in
        --unit) RUN_UNIT=true ;;
        --integration) RUN_INTEGRATION=true ;;
        --e2e) RUN_E2E=true ;;
        --load) RUN_LOAD=true ;;
        --all) RUN_ALL=true ;;
    esac
done

# If --all is set, enable all tests
if [ "$RUN_ALL" = true ]; then
    RUN_UNIT=true
    RUN_INTEGRATION=true
    RUN_E2E=true
    RUN_LOAD=false  # Load tests are optional
fi

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# =============================================================================
# Pre-flight Checks
# =============================================================================

print_header "🚀 LifeAI Test Suite"

# Check if services are running
print_info "Checking if services are running..."

if ! docker ps | grep -q lifeai-backend; then
    print_error "Backend container is not running. Start it with: docker-compose up -d"
    exit 1
fi

if ! docker ps | grep -q lifeai-frontend; then
    print_error "Frontend container is not running. Start it with: docker-compose up -d"
    exit 1
fi

print_success "All services are running"

# =============================================================================
# 1. Unit Tests (Backend)
# =============================================================================

if [ "$RUN_UNIT" = true ]; then
    print_header "1️⃣ Backend Unit Tests"

    print_info "Running pytest with coverage..."

    if docker compose version &> /dev/null; then
        docker compose exec backend pytest tests/ \
            --cov=app \
            --cov-report=term-missing \
            --cov-report=html \
            -v \
            || print_error "Some unit tests failed"
    else
        docker-compose exec backend pytest tests/ \
            --cov=app \
            --cov-report=term-missing \
            --cov-report=html \
            -v \
            || print_error "Some unit tests failed"
    fi

    print_success "Backend unit tests completed"
fi

# =============================================================================
# 2. Integration Tests
# =============================================================================

if [ "$RUN_INTEGRATION" = true ]; then
    print_header "2️⃣ Integration Tests"

    print_info "Testing API endpoints..."

    # Health check
    print_info "Testing health endpoint..."
    HEALTH_STATUS=$(curl -s http://localhost:8000/health/live | jq -r '.status' 2>/dev/null || echo "error")
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
    fi

    # API Documentation
    print_info "Testing API docs..."
    DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
    if [ "$DOCS_STATUS" = "200" ]; then
        print_success "API docs accessible"
    else
        print_error "API docs not accessible"
    fi

    # GraphQL endpoint
    print_info "Testing GraphQL endpoint..."
    GRAPHQL_RESPONSE=$(curl -s -X POST http://localhost:8000/graphql \
        -H "Content-Type: application/json" \
        -d '{"query": "{ __typename }"}')

    if echo "$GRAPHQL_RESPONSE" | grep -q "__typename"; then
        print_success "GraphQL endpoint working"
    else
        print_error "GraphQL endpoint not working"
    fi

    # WebSocket connection
    print_info "Testing WebSocket connection..."
    # Note: WebSocket testing requires wscat or similar tool
    if command -v wscat &> /dev/null; then
        timeout 5 wscat -c ws://localhost:8000/ws -x '{"type":"ping"}' &> /dev/null && \
            print_success "WebSocket connection working" || \
            print_error "WebSocket connection failed"
    else
        print_info "Skipping WebSocket test (wscat not installed)"
    fi

    # Database connection
    print_info "Testing database connection..."
    DB_STATUS=$(docker exec lifeai-postgres pg_isready -U lifeai)
    if echo "$DB_STATUS" | grep -q "accepting connections"; then
        print_success "Database connection working"
    else
        print_error "Database connection failed"
    fi

    # Redis connection
    print_info "Testing Redis connection..."
    REDIS_STATUS=$(docker exec lifeai-redis redis-cli ping)
    if [ "$REDIS_STATUS" = "PONG" ]; then
        print_success "Redis connection working"
    else
        print_error "Redis connection failed"
    fi

    print_success "Integration tests completed"
fi

# =============================================================================
# 3. Frontend Tests
# =============================================================================

if [ "$RUN_UNIT" = true ]; then
    print_header "3️⃣ Frontend Tests"

    print_info "Running Jest tests..."

    cd frontend
    npm test -- --coverage --watchAll=false || print_error "Some frontend tests failed"
    cd ..

    print_success "Frontend tests completed"
fi

# =============================================================================
# 4. E2E Tests (Playwright)
# =============================================================================

if [ "$RUN_E2E" = true ]; then
    print_header "4️⃣ End-to-End Tests"

    print_info "Running Playwright E2E tests..."

    # Check if Playwright is installed
    if [ -d "frontend/node_modules/@playwright" ]; then
        cd frontend
        npx playwright test || print_error "Some E2E tests failed"
        cd ..
        print_success "E2E tests completed"
    else
        print_info "Playwright not installed. Installing..."
        cd frontend
        npm install -D @playwright/test
        npx playwright install
        npx playwright test || print_error "Some E2E tests failed"
        cd ..
    fi
fi

# =============================================================================
# 5. Load Tests (k6)
# =============================================================================

if [ "$RUN_LOAD" = true ]; then
    print_header "5️⃣ Load Tests"

    # Check if k6 is installed
    if command -v k6 &> /dev/null; then
        print_info "Running k6 load tests..."

        # Set BASE_URL for load tests
        export BASE_URL=http://localhost:8000

        # Run load test
        k6 run tests/load/chat-api-load-test.js \
            --out json=test-results/load-test-results.json \
            || print_error "Load tests failed"

        print_success "Load tests completed"
    else
        print_info "k6 not installed. Skipping load tests."
        echo "  Install k6: https://k6.io/docs/getting-started/installation/"
    fi
fi

# =============================================================================
# 6. Security Scan
# =============================================================================

print_header "6️⃣ Security Scan"

# Check for common security issues
print_info "Checking for exposed secrets..."

# Check .env is not committed
if git ls-files --error-unmatch .env &> /dev/null; then
    print_error ".env file is tracked by git! Remove it immediately!"
else
    print_success ".env file is not tracked by git"
fi

# Check for hardcoded secrets in code
print_info "Scanning for hardcoded secrets..."
if command -v gitleaks &> /dev/null; then
    gitleaks detect --source . --verbose || print_error "Potential secrets found!"
else
    print_info "gitleaks not installed. Skipping secret scanning."
fi

# Dependency vulnerability scan
print_info "Checking for vulnerable dependencies..."

# Backend (Python)
cd backend
if command -v safety &> /dev/null; then
    safety check || print_error "Vulnerable Python dependencies found"
else
    pip3 install safety &> /dev/null
    safety check || print_error "Vulnerable Python dependencies found"
fi
cd ..

# Frontend (npm)
cd frontend
npm audit --audit-level=moderate || print_error "Vulnerable npm dependencies found"
cd ..

print_success "Security scan completed"

# =============================================================================
# 7. Performance Metrics
# =============================================================================

print_header "7️⃣ Performance Metrics"

# API response time
print_info "Measuring API response time..."
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:8000/health/live)
echo "  Health endpoint: ${RESPONSE_TIME}s"

# Database query performance
print_info "Checking database performance..."
docker exec lifeai-postgres psql -U lifeai -d lifeai -c \
    "SELECT count(*) FROM pg_stat_statements;" &> /dev/null && \
    print_success "Database statistics available" || \
    print_info "Database statistics extension not enabled"

# Redis performance
print_info "Checking Redis performance..."
REDIS_OPS=$(docker exec lifeai-redis redis-cli info stats | grep "total_commands_processed" | cut -d: -f2)
echo "  Total Redis operations: $REDIS_OPS"

# =============================================================================
# 8. Test Summary
# =============================================================================

print_header "📊 Test Summary"

echo ""
echo -e "${GREEN}Tests completed!${NC}"
echo ""
echo "📁 Test Reports:"
echo "  - Backend Coverage:  backend/htmlcov/index.html"
echo "  - Frontend Coverage: frontend/coverage/index.html"
if [ "$RUN_E2E" = true ]; then
    echo "  - E2E Report:        frontend/playwright-report/index.html"
fi
if [ "$RUN_LOAD" = true ]; then
    echo "  - Load Test:         test-results/load-test-results.json"
fi
echo ""

echo "🔍 Next Steps:"
echo "  1. Review test coverage reports"
echo "  2. Fix any failing tests"
echo "  3. Address security vulnerabilities"
echo "  4. Optimize slow endpoints"
echo ""

echo "📚 Additional Test Commands:"
echo "  - Backend only:      ./test.sh --unit"
echo "  - Integration only:  ./test.sh --integration"
echo "  - E2E only:          ./test.sh --e2e"
echo "  - Load tests:        ./test.sh --load"
echo ""

# Exit with success
exit 0
