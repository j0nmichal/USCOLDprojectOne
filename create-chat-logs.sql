-- Chat analytics log table
-- Run in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS chat_logs (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id      text NOT NULL,
  turn_number     int  NOT NULL,
  role            text NOT NULL CHECK (role IN ('user','assistant')),
  message         text NOT NULL,
  facilities      text[],
  guardrail_hit   boolean DEFAULT false,
  created_at      timestamptz DEFAULT now()
);

-- Index for fast session lookups and time-range queries
CREATE INDEX IF NOT EXISTS chat_logs_session_idx    ON chat_logs (session_id);
CREATE INDEX IF NOT EXISTS chat_logs_created_at_idx ON chat_logs (created_at DESC);

-- Allow public inserts (logging from browser) and reads (admin panel)
ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow_insert" ON chat_logs FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "allow_select" ON chat_logs FOR SELECT TO anon USING (true);
