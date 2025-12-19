-- Initialize LifeAI database
-- This script runs on first PostgreSQL startup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create indexes for better performance
-- Note: Additional indexes will be created by Alembic migrations

-- Set timezone
SET timezone = 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE lifeai TO lifeai;

-- Log initialization
DO $$
BEGIN
  RAISE NOTICE 'LifeAI database initialized successfully';
END $$;
