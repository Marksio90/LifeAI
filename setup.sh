#!/bin/bash
# =============================================================================
# 🚀 LifeAI - Automated Setup Script
# =============================================================================
# This script automates the complete setup of LifeAI platform
# Usage: ./setup.sh [--skip-env] [--skip-deps] [--production]
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
SKIP_ENV=false
SKIP_DEPS=false
PRODUCTION=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --skip-env)
            SKIP_ENV=true
            shift
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --production)
            PRODUCTION=true
            shift
            ;;
    esac
done

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

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        return 1
    else
        print_success "$1 is installed"
        return 0
    fi
}

generate_secret_key() {
    openssl rand -hex 32
}

# =============================================================================
# 1. Check Prerequisites
# =============================================================================

print_header "1️⃣ Checking Prerequisites"

MISSING_DEPS=false

if ! check_command "docker"; then MISSING_DEPS=true; fi
if ! check_command "docker-compose" && ! docker compose version &> /dev/null; then
    print_error "docker-compose is not installed"
    MISSING_DEPS=true
fi
if ! check_command "node"; then MISSING_DEPS=true; fi
if ! check_command "npm"; then MISSING_DEPS=true; fi
if ! check_command "python3"; then MISSING_DEPS=true; fi
if ! check_command "pip3"; then MISSING_DEPS=true; fi

if [ "$MISSING_DEPS" = true ]; then
    print_error "Missing required dependencies. Please install them first."
    echo ""
    echo "Installation guides:"
    echo "  - Docker: https://docs.docker.com/get-docker/"
    echo "  - Node.js: https://nodejs.org/"
    echo "  - Python: https://www.python.org/"
    exit 1
fi

print_success "All prerequisites are installed!"

# =============================================================================
# 2. Environment Setup
# =============================================================================

if [ "$SKIP_ENV" = false ]; then
    print_header "2️⃣ Setting Up Environment Variables"

    if [ -f .env ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
        else
            rm .env
            cp .env.example .env
            print_success "Created new .env file from template"
        fi
    else
        cp .env.example .env
        print_success "Created .env file from template"
    fi

    # Generate secret key
    print_info "Generating SECRET_KEY..."
    SECRET_KEY=$(generate_secret_key)

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    fi
    print_success "Generated SECRET_KEY"

    # Prompt for OpenAI API Key
    echo ""
    print_warning "IMPORTANT: You need to set your OpenAI API Key"
    echo "Get your key from: https://platform.openai.com/api-keys"
    read -p "Enter your OpenAI API Key (or press Enter to skip): " OPENAI_KEY

    if [ ! -z "$OPENAI_KEY" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/sk-your-openai-api-key-here/$OPENAI_KEY/" .env
        else
            sed -i "s/sk-your-openai-api-key-here/$OPENAI_KEY/" .env
        fi
        print_success "OpenAI API Key configured"
    else
        print_warning "Skipped OpenAI API Key - you'll need to set it manually in .env"
    fi

    # Generate strong password for PostgreSQL
    print_info "Generating PostgreSQL password..."
    POSTGRES_PASSWORD=$(openssl rand -base64 24)

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/change-this-strong-password/$POSTGRES_PASSWORD/g" .env
    else
        sed -i "s/change-this-strong-password/$POSTGRES_PASSWORD/g" .env
    fi
    print_success "Generated PostgreSQL password"

else
    print_info "Skipping environment setup (--skip-env flag)"
fi

# =============================================================================
# 3. Install Dependencies
# =============================================================================

if [ "$SKIP_DEPS" = false ]; then
    print_header "3️⃣ Installing Dependencies"

    # Backend dependencies
    print_info "Installing backend dependencies..."
    cd backend

    if [ "$PRODUCTION" = true ]; then
        pip3 install -r requirements.txt
    else
        pip3 install -r requirements.txt
    fi

    cd ..
    print_success "Backend dependencies installed"

    # Frontend dependencies
    print_info "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    print_success "Frontend dependencies installed"

else
    print_info "Skipping dependency installation (--skip-deps flag)"
fi

# =============================================================================
# 4. Database Initialization
# =============================================================================

print_header "4️⃣ Database Setup"

# Create init script if it doesn't exist
mkdir -p backend/scripts

if [ ! -f backend/scripts/init-db.sql ]; then
    cat > backend/scripts/init-db.sql << 'EOF'
-- LifeAI Database Initialization Script
-- This runs automatically when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database user (if not exists)
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'lifeai'
   ) THEN
      CREATE ROLE lifeai WITH LOGIN PASSWORD 'changeme';
   END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE lifeai TO lifeai;

-- Success message
SELECT 'LifeAI database initialized successfully!' as message;
EOF
    print_success "Created database initialization script"
else
    print_info "Database initialization script already exists"
fi

# =============================================================================
# 5. Docker Setup
# =============================================================================

print_header "5️⃣ Building Docker Containers"

# Stop existing containers
print_info "Stopping existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Build containers
print_info "Building Docker images (this may take a few minutes)..."
if docker compose version &> /dev/null; then
    docker compose build
else
    docker-compose build
fi

print_success "Docker images built successfully"

# =============================================================================
# 6. Start Services
# =============================================================================

print_header "6️⃣ Starting Services"

print_info "Starting all services..."
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

print_success "All services started!"

# Wait for services to be healthy
print_info "Waiting for services to be ready..."
sleep 10

# Check service health
print_info "Checking service health..."

# Check PostgreSQL
if docker exec lifeai-postgres pg_isready -U lifeai &> /dev/null; then
    print_success "PostgreSQL is ready"
else
    print_warning "PostgreSQL is not ready yet"
fi

# Check Redis
if docker exec lifeai-redis redis-cli ping &> /dev/null; then
    print_success "Redis is ready"
else
    print_warning "Redis is not ready yet"
fi

# =============================================================================
# 7. Database Migration
# =============================================================================

print_header "7️⃣ Running Database Migrations"

print_info "Running Alembic migrations..."
if docker compose version &> /dev/null; then
    docker compose exec -T backend alembic upgrade head 2>/dev/null || print_warning "Migrations not configured yet"
else
    docker-compose exec -T backend alembic upgrade head 2>/dev/null || print_warning "Migrations not configured yet"
fi

# =============================================================================
# 8. Verification
# =============================================================================

print_header "8️⃣ Verifying Installation"

# Check if backend is responding
sleep 5
if curl -s http://localhost:8000/health/live > /dev/null; then
    print_success "Backend API is responding"
else
    print_warning "Backend API is not responding yet (may need more time)"
fi

# Check if frontend is responding
if curl -s http://localhost:3000 > /dev/null; then
    print_success "Frontend is responding"
else
    print_warning "Frontend is not responding yet (may need more time)"
fi

# =============================================================================
# 9. Summary
# =============================================================================

print_header "🎉 Setup Complete!"

echo ""
echo -e "${GREEN}LifeAI has been successfully set up!${NC}"
echo ""
echo "🌐 Services are running at:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - GraphQL:   http://localhost:8000/graphql"
echo ""
echo "📋 Next Steps:"
echo "  1. Visit http://localhost:3000 to access the application"
echo "  2. Review .env file and update any missing values"
echo "  3. Run './test.sh' to verify all features"
echo ""
echo "🛠️ Useful Commands:"
echo "  - View logs:        docker-compose logs -f"
echo "  - Stop services:    docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Run tests:        ./test.sh"
echo ""

if [ -z "$OPENAI_KEY" ] || [ "$OPENAI_KEY" = "sk-your-openai-api-key-here" ]; then
    print_warning "Remember to set your OpenAI API Key in .env file!"
fi

echo -e "${BLUE}For detailed documentation, see INSTALLATION.md${NC}"
echo ""
