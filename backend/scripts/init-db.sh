#!/bin/bash
# Database initialization script for Docker container

set -e

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h postgres -U lifeai > /dev/null 2>&1; do
    sleep 1
done

echo "Running Alembic migrations..."
cd /app
alembic upgrade head

echo "Database initialization complete!"
