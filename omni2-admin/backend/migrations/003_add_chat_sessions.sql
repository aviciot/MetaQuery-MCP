-- Migration: Add chat sessions and messages tables
-- Description: Tables for storing chat history

CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_pinned BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'bot')),
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    tool_calls INTEGER DEFAULT 0,
    tools_used JSONB DEFAULT '[]'::jsonb,
    message_metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for performance
CREATE INDEX idx_chat_sessions_admin_user_id ON chat_sessions(admin_user_id);
CREATE INDEX idx_chat_sessions_updated_at ON chat_sessions(updated_at DESC);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);

-- Comments
COMMENT ON TABLE chat_sessions IS 'Stores chat conversation sessions';
COMMENT ON TABLE chat_messages IS 'Stores individual messages in chat sessions';
COMMENT ON COLUMN chat_sessions.is_pinned IS 'Whether the session is pinned to the top';
COMMENT ON COLUMN chat_messages.message_metadata IS 'Additional message data like reactions, edits, etc.';
