-- ============================================================================
-- AI Second Brain - Supabase Database Schema
-- ============================================================================
-- Run these SQL statements in your Supabase SQL Editor
-- Project: ahhkjfisxgtjcufqxkff
-- ============================================================================

-- 1. Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_session
        FOREIGN KEY (session_id) 
        REFERENCES chat_sessions(session_id)
        ON DELETE CASCADE
);

-- 3. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at);

-- 4. Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 5. Create policies to allow all operations (adjust based on your auth needs)
-- For now, allowing all operations. Modify these when you add authentication.
CREATE POLICY "Allow all operations on chat_sessions" ON chat_sessions
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on messages" ON messages
    FOR ALL USING (true) WITH CHECK (true);

-- 6. Create a function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 7. Create trigger to automatically update updated_at
CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Verification Queries (run these to verify tables were created)
-- ============================================================================

-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('chat_sessions', 'messages');

-- Check indexes
SELECT indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('chat_sessions', 'messages');

-- ============================================================================
-- Test Data (Optional - remove if not needed)
-- ============================================================================

-- Insert a test session
-- INSERT INTO chat_sessions (session_id, title) 
-- VALUES ('test-session-1', 'Test Chat');

-- Insert a test message
-- INSERT INTO messages (session_id, sender, message) 
-- VALUES ('test-session-1', 'user', 'Hello!');

-- ============================================================================
-- Done! Your database is ready.
-- ============================================================================
