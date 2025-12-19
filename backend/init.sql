-- LifeAI Database Schema
-- Timeline table for storing conversation snapshots

CREATE TABLE IF NOT EXISTS timeline (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    summary TEXT,
    themes JSONB DEFAULT '[]'::jsonb,
    core_question TEXT,
    emotional_tone VARCHAR(50),
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1)
);

-- Index for faster queries by date
CREATE INDEX IF NOT EXISTS idx_timeline_created_at ON timeline(created_at DESC);

-- Index for emotional tone filtering
CREATE INDEX IF NOT EXISTS idx_timeline_emotional_tone ON timeline(emotional_tone);
