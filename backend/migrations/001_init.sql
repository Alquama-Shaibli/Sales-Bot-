-- ============================================================
-- 001_init.sql — Initial Database Schema
-- EnterpriseLead AI — FlowZint Hackathon 2026
-- Run once on fresh database to set up all tables + indexes
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Enums ───────────────────────────────────────────────────────────────────

DO $$ BEGIN
    CREATE TYPE conversation_status AS ENUM ('active', 'completed', 'converted', 'abandoned');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE lead_status AS ENUM ('hot', 'warm', 'cold');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE intent_level AS ENUM ('High', 'Medium', 'Low');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ── Table: conversations ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS conversations (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status      conversation_status NOT NULL DEFAULT 'active',
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);

-- ── Table: messages ──────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS messages (
    id                  SERIAL PRIMARY KEY,
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role                message_role NOT NULL,
    content             TEXT NOT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at ASC);
CREATE INDEX IF NOT EXISTS idx_messages_conv_created ON messages(conversation_id, created_at ASC);

-- ── Table: leads ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS leads (
    id                  SERIAL PRIMARY KEY,
    conversation_id     UUID NOT NULL UNIQUE REFERENCES conversations(id) ON DELETE CASCADE,
    email               VARCHAR(255),
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    company             VARCHAR(255),
    job_title           VARCHAR(255),
    score               INTEGER NOT NULL DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    icp_fit             INTEGER NOT NULL DEFAULT 0 CHECK (icp_fit >= 0 AND icp_fit <= 100),
    intent_level        intent_level,
    timeline            VARCHAR(100),
    status              lead_status,
    hubspot_id          VARCHAR(100),
    hubspot_synced      BOOLEAN NOT NULL DEFAULT FALSE,
    alert_sent          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_hubspot_id ON leads(hubspot_id);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);

-- ── Table: lead_scores ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS lead_scores (
    id                  SERIAL PRIMARY KEY,
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    overall_score       INTEGER NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    icp_fit             INTEGER NOT NULL CHECK (icp_fit >= 0 AND icp_fit <= 100),
    intent_signals      INTEGER NOT NULL CHECK (intent_signals >= 0 AND intent_signals <= 100),
    timeline            INTEGER NOT NULL CHECK (timeline >= 0 AND timeline <= 100),
    authority           INTEGER NOT NULL CHECK (authority >= 0 AND authority <= 100),
    engagement          INTEGER NOT NULL CHECK (engagement >= 0 AND engagement <= 100),
    reasoning           TEXT,
    recommendation      VARCHAR(50),
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lead_scores_conversation_id ON lead_scores(conversation_id);
CREATE INDEX IF NOT EXISTS idx_lead_scores_overall ON lead_scores(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_lead_scores_created_at ON lead_scores(created_at DESC);

-- ── Reporting Views ──────────────────────────────────────────────────────────

-- Hot leads dashboard view
CREATE OR REPLACE VIEW v_hot_leads AS
SELECT
    l.id,
    l.email,
    l.company,
    l.job_title,
    l.score,
    l.icp_fit,
    l.intent_level,
    l.timeline,
    l.hubspot_id,
    l.hubspot_synced,
    l.alert_sent,
    l.created_at,
    ls.reasoning,
    ls.recommendation
FROM leads l
LEFT JOIN lead_scores ls ON ls.conversation_id = l.conversation_id
WHERE l.score >= 75
ORDER BY l.score DESC;

-- Pipeline summary view
CREATE OR REPLACE VIEW v_pipeline_summary AS
SELECT
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE status = 'hot') AS hot_leads,
    COUNT(*) FILTER (WHERE status = 'warm') AS warm_leads,
    COUNT(*) FILTER (WHERE status = 'cold') AS cold_leads,
    ROUND(AVG(score), 1) AS average_score,
    COUNT(*) FILTER (WHERE hubspot_synced = TRUE) AS synced_to_hubspot,
    COUNT(*) FILTER (WHERE alert_sent = TRUE) AS alerts_sent
FROM leads;

-- Daily conversation metrics view
CREATE OR REPLACE VIEW v_daily_metrics AS
SELECT
    DATE(c.created_at) AS date,
    COUNT(DISTINCT c.id) AS conversations,
    COUNT(DISTINCT l.id) AS leads_qualified,
    ROUND(AVG(l.score), 1) AS avg_lead_score,
    COUNT(DISTINCT l.id) FILTER (WHERE l.status = 'hot') AS hot_leads
FROM conversations c
LEFT JOIN leads l ON l.conversation_id = c.id
GROUP BY DATE(c.created_at)
ORDER BY date DESC;
