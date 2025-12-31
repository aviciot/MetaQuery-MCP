-- ============================================================
-- Business Logic Knowledge Base Schema
-- ============================================================
-- PostgreSQL 14+ required
-- This schema stores discovered database metadata and business context
-- to enable intelligent query explanation with caching
-- ============================================================

-- ============================================================
-- Table Knowledge
-- ============================================================
-- Stores discovered information about database tables
CREATE TABLE IF NOT EXISTS table_knowledge (
    id SERIAL PRIMARY KEY,
    
    -- Source identification
    db_name VARCHAR(100) NOT NULL,           -- Oracle DB preset name
    db_type VARCHAR(50) DEFAULT 'oracle',    -- oracle, mysql
    owner VARCHAR(128) NOT NULL,             -- Schema owner
    table_name VARCHAR(128) NOT NULL,        -- Table name
    
    -- Oracle-sourced metadata
    oracle_comment TEXT,                     -- From ALL_TAB_COMMENTS
    num_rows BIGINT,                         -- Approximate row count
    is_partitioned BOOLEAN DEFAULT FALSE,
    partition_type VARCHAR(50),              -- RANGE, LIST, HASH
    partition_key_columns TEXT[],            -- Partition key columns
    
    -- Inferred business context (LLM-generated)
    inferred_entity_type VARCHAR(100),       -- "customer", "transaction", "order"
    inferred_domain VARCHAR(100),            -- "payments", "inventory", "HR"
    business_description TEXT,               -- Human-readable description
    business_purpose TEXT,                   -- What this table is used for
    
    -- Column details (JSON for flexibility)
    columns JSONB DEFAULT '[]',              -- [{name, type, nullable, comment, inferred_meaning}]
    primary_key_columns TEXT[],
    
    -- Discovery metadata
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_refreshed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    refresh_count INTEGER DEFAULT 1,
    confidence_score FLOAT DEFAULT 0.5,      -- How confident we are in inference
    
    -- Unique constraint
    CONSTRAINT uq_table_knowledge UNIQUE (db_name, owner, table_name)
);

-- Indexes
CREATE INDEX idx_table_knowledge_db ON table_knowledge(db_name);
CREATE INDEX idx_table_knowledge_domain ON table_knowledge(inferred_domain);
CREATE INDEX idx_table_knowledge_entity ON table_knowledge(inferred_entity_type);
CREATE INDEX idx_table_knowledge_refresh ON table_knowledge(last_refreshed);

COMMENT ON TABLE table_knowledge IS 'Cached business context for database tables';

-- ============================================================
-- Relationship Knowledge
-- ============================================================
-- Stores discovered relationships between tables
CREATE TABLE IF NOT EXISTS relationship_knowledge (
    id SERIAL PRIMARY KEY,
    
    -- Source identification
    db_name VARCHAR(100) NOT NULL,
    
    -- Relationship endpoints
    from_owner VARCHAR(128) NOT NULL,
    from_table VARCHAR(128) NOT NULL,
    from_columns TEXT[] NOT NULL,            -- FK columns
    
    to_owner VARCHAR(128) NOT NULL,
    to_table VARCHAR(128) NOT NULL,
    to_columns TEXT[] NOT NULL,              -- PK/UK columns
    
    -- Relationship metadata
    relationship_type VARCHAR(50) NOT NULL,  -- FK, INFERRED, LOOKUP
    constraint_name VARCHAR(128),            -- Oracle constraint name if FK
    cardinality VARCHAR(20),                 -- 1:1, 1:N, N:M
    is_lookup BOOLEAN DEFAULT FALSE,         -- Is to_table a small lookup table?
    
    -- Business context (LLM-generated)
    business_meaning TEXT,                   -- "customer places orders"
    relationship_role VARCHAR(100),          -- "parent", "lookup", "audit"
    
    -- Discovery metadata
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_refreshed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint
    CONSTRAINT uq_relationship UNIQUE (db_name, from_owner, from_table, to_owner, to_table, from_columns)
);

-- Indexes
CREATE INDEX idx_relationship_db ON relationship_knowledge(db_name);
CREATE INDEX idx_relationship_from ON relationship_knowledge(from_owner, from_table);
CREATE INDEX idx_relationship_to ON relationship_knowledge(to_owner, to_table);

COMMENT ON TABLE relationship_knowledge IS 'Cached FK and inferred relationships';

-- ============================================================
-- Query Explanations Cache
-- ============================================================
-- Caches generated business explanations for queries
CREATE TABLE IF NOT EXISTS query_explanations (
    id SERIAL PRIMARY KEY,
    
    -- Query identification
    sql_fingerprint VARCHAR(64) NOT NULL,    -- Hash of normalized SQL
    db_name VARCHAR(100) NOT NULL,
    
    -- Original query (for reference)
    sql_text TEXT NOT NULL,
    sql_normalized TEXT,                     -- Normalized version
    
    -- Tables involved
    tables_involved JSONB DEFAULT '[]',      -- [{owner, table}]
    
    -- Generated explanation
    business_explanation TEXT NOT NULL,      -- Full LLM-generated explanation
    query_purpose TEXT,                      -- One-line summary
    data_flow_description TEXT,              -- How data flows through tables
    domain_tags TEXT[],                      -- ["payments", "settlements"]
    
    -- Usage tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    hit_count INTEGER DEFAULT 1,
    
    -- Quality tracking
    was_helpful BOOLEAN,                     -- User feedback
    feedback_notes TEXT,
    
    -- Unique constraint
    CONSTRAINT uq_query_explanation UNIQUE (sql_fingerprint, db_name)
);

-- Indexes
CREATE INDEX idx_query_exp_fingerprint ON query_explanations(sql_fingerprint);
CREATE INDEX idx_query_exp_db ON query_explanations(db_name);
CREATE INDEX idx_query_exp_accessed ON query_explanations(last_accessed);
CREATE INDEX idx_query_exp_domain ON query_explanations USING GIN(domain_tags);

COMMENT ON TABLE query_explanations IS 'Cached business explanations for SQL queries';

-- ============================================================
-- Domain Glossary
-- ============================================================
-- Business terms and their meanings discovered across queries
CREATE TABLE IF NOT EXISTS domain_glossary (
    id SERIAL PRIMARY KEY,
    
    -- Term identification
    term VARCHAR(100) NOT NULL,              -- "settlement", "chargeback"
    domain VARCHAR(100) NOT NULL,            -- "payments", "inventory"
    
    -- Definition
    definition TEXT NOT NULL,                -- Business meaning
    examples TEXT[],                         -- Example contexts
    related_terms TEXT[],                    -- Related business terms
    
    -- Where it appears
    example_tables TEXT[],                   -- Tables where this concept appears
    example_columns TEXT[],                  -- Columns with this term
    
    -- Metadata
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    occurrence_count INTEGER DEFAULT 1,
    
    -- Unique constraint
    CONSTRAINT uq_glossary_term UNIQUE (term, domain)
);

-- Indexes
CREATE INDEX idx_glossary_domain ON domain_glossary(domain);
CREATE INDEX idx_glossary_term ON domain_glossary(term);

COMMENT ON TABLE domain_glossary IS 'Business domain terminology';

-- ============================================================
-- Column Patterns
-- ============================================================
-- Stores discovered patterns in column naming and values
CREATE TABLE IF NOT EXISTS column_patterns (
    id SERIAL PRIMARY KEY,
    
    -- Pattern identification
    column_name_pattern VARCHAR(100) NOT NULL,  -- "STATUS", "*_ID", "*_DATE"
    
    -- Inferred semantics
    semantic_type VARCHAR(100),              -- "identifier", "timestamp", "status_code"
    typical_values JSONB,                    -- Sample values seen
    value_meanings JSONB,                    -- {"P": "Pending", "A": "Approved"}
    
    -- Statistics
    occurrence_count INTEGER DEFAULT 1,
    databases_seen TEXT[],
    
    -- Metadata
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT uq_column_pattern UNIQUE (column_name_pattern)
);

-- Index
CREATE INDEX idx_column_patterns_semantic ON column_patterns(semantic_type);

COMMENT ON TABLE column_patterns IS 'Learned patterns in column naming conventions';

-- ============================================================
-- Discovery Log
-- ============================================================
-- Tracks discovery operations for debugging and stats
CREATE TABLE IF NOT EXISTS discovery_log (
    id SERIAL PRIMARY KEY,
    
    -- Operation details
    operation_type VARCHAR(50) NOT NULL,     -- "table_discovery", "relationship_scan", "explain_query"
    db_name VARCHAR(100) NOT NULL,
    
    -- What was discovered
    tables_discovered INTEGER DEFAULT 0,
    relationships_discovered INTEGER DEFAULT 0,
    cache_hits INTEGER DEFAULT 0,
    cache_misses INTEGER DEFAULT 0,
    
    -- Performance
    duration_ms INTEGER,
    oracle_queries_executed INTEGER DEFAULT 0,
    
    -- Outcome
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_discovery_log_db ON discovery_log(db_name);
CREATE INDEX idx_discovery_log_created ON discovery_log(created_at);

COMMENT ON TABLE discovery_log IS 'Audit log of discovery operations';

-- ============================================================
-- Helper Function: Update timestamp
-- ============================================================
CREATE OR REPLACE FUNCTION update_last_refreshed()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_refreshed = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for auto-updating last_refreshed
CREATE TRIGGER trg_table_knowledge_refresh
    BEFORE UPDATE ON table_knowledge
    FOR EACH ROW EXECUTE FUNCTION update_last_refreshed();

CREATE TRIGGER trg_relationship_refresh
    BEFORE UPDATE ON relationship_knowledge
    FOR EACH ROW EXECUTE FUNCTION update_last_refreshed();
