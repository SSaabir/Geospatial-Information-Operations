-- ================================================
-- Geospatial Information Operations Database Schema
-- PostgreSQL Database: GISDb
-- Last Updated: October 16, 2025
-- ================================================

-- ================================================
-- AUTHENTICATION & USER MANAGEMENT
-- ================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    tier VARCHAR(20) DEFAULT 'free',
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_tier ON users(tier);

-- Authentication events log
CREATE TABLE IF NOT EXISTS auth_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50),
    user_id VARCHAR(50),
    ip_address VARCHAR(45),
    success BOOLEAN,
    failure_reason VARCHAR(200),
    session_id VARCHAR(100),
    user_agent TEXT,
    geolocation JSONB
);

CREATE INDEX IF NOT EXISTS idx_auth_events_user ON auth_events(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_events_timestamp ON auth_events(timestamp DESC);

-- ================================================
-- WEATHER & CLIMATE DATA
-- ================================================

-- Historical weather data (52,435 records from 1997-2025)
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    date DATE,
    tempmax DOUBLE PRECISION,
    tempmin DOUBLE PRECISION,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    precipsum DOUBLE PRECISION,
    rain BOOLEAN,
    snow BOOLEAN,
    snowdepth DOUBLE PRECISION,
    windgust DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    winddir DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    cloudcover DOUBLE PRECISION,
    visibility DOUBLE PRECISION,
    solarradiation DOUBLE PRECISION,
    solarenergy DOUBLE PRECISION,
    uvindex DOUBLE PRECISION,
    sunrise TIME WITHOUT TIME ZONE,
    sunset TIME WITHOUT TIME ZONE,
    moonphase DOUBLE PRECISION,
    conditions VARCHAR(255),
    description TEXT,
    icon VARCHAR(50),
    country VARCHAR(100),
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_weather_city ON weather_data(city);
CREATE INDEX IF NOT EXISTS idx_weather_date ON weather_data(date DESC);
CREATE INDEX IF NOT EXISTS idx_weather_city_date ON weather_data(city, date DESC);

-- Air quality data
CREATE TABLE IF NOT EXISTS air_quality_data (
    id SERIAL PRIMARY KEY,
    country TEXT,
    statedistrict TEXT,
    datetime DATE,
    pm10 DOUBLE PRECISION,
    pm2_5 DOUBLE PRECISION,
    carbon_monoxide DOUBLE PRECISION,
    ozone DOUBLE PRECISION,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    source TEXT
);

CREATE INDEX IF NOT EXISTS idx_air_quality_location ON air_quality_data(statedistrict, datetime DESC);

-- ================================================
-- USAGE & BILLING
-- ================================================

-- Usage metrics tracking
CREATE TABLE IF NOT EXISTS usage_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_calls INTEGER NOT NULL DEFAULT 0,
    reports_generated INTEGER NOT NULL DEFAULT 0,
    data_downloads INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_usage_user ON usage_metrics(user_id);

-- Payments and subscriptions
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC NOT NULL,
    plan VARCHAR(50) NOT NULL,
    recurring BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_expires ON payments(expires_at);

-- Checkout sessions (for payment processing)
CREATE TABLE IF NOT EXISTS checkout_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan VARCHAR(50) NOT NULL,
    amount NUMERIC NOT NULL,
    recurring BOOLEAN DEFAULT false,
    paid BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT false,
    last4 VARCHAR(4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paid_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_checkout_user ON checkout_sessions(user_id);

-- ================================================
-- NOTIFICATIONS
-- ================================================

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20),
    subject VARCHAR(255),
    message TEXT,
    metadata JSONB,
    read BOOLEAN DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(user_id, read);

-- ================================================
-- NEWS & CONTENT
-- ================================================

CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    content TEXT,
    url VARCHAR(1000) NOT NULL UNIQUE,
    source VARCHAR(200) NOT NULL,
    author VARCHAR(200),
    published_at TIMESTAMP WITH TIME ZONE,
    image_url VARCHAR(1000),
    category VARCHAR(100),
    keywords JSON,
    relevance_score INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_category ON news_articles(category);
CREATE INDEX IF NOT EXISTS idx_news_active ON news_articles(is_active, published_at DESC);

-- ================================================
-- SECURITY & MONITORING
-- ================================================

-- API access log
CREATE TABLE IF NOT EXISTS api_access_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    endpoint VARCHAR(200),
    method VARCHAR(10),
    user_id VARCHAR(50),
    ip_address VARCHAR(45),
    user_agent TEXT,
    response_code INTEGER,
    response_time DOUBLE PRECISION,
    request_size INTEGER,
    response_size INTEGER,
    threat_score DOUBLE PRECISION DEFAULT 0.0
);

CREATE INDEX IF NOT EXISTS idx_api_log_timestamp ON api_access_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_log_user ON api_access_log(user_id, timestamp DESC);

-- Security alerts
CREATE TABLE IF NOT EXISTS security_alerts (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    threat_type VARCHAR(50),
    severity VARCHAR(20),
    source VARCHAR(100),
    description TEXT,
    affected_data VARCHAR(200),
    remediation TEXT,
    user_id VARCHAR(50),
    ip_address VARCHAR(45),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_security_alerts_severity ON security_alerts(severity, timestamp DESC);

-- Security incidents
CREATE TABLE IF NOT EXISTS security_incidents (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(50),
    threat_level VARCHAR(20),
    title VARCHAR(200),
    description TEXT,
    source_ip VARCHAR(45),
    user_id VARCHAR(50),
    affected_resources JSONB,
    indicators JSONB,
    response_actions JSONB,
    status VARCHAR(20) DEFAULT 'open',
    assigned_to VARCHAR(50),
    resolution_notes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_security_incidents_status ON security_incidents(status, timestamp DESC);

-- Security audit log
CREATE TABLE IF NOT EXISTS security_audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    action VARCHAR(100),
    user_id VARCHAR(50),
    ip_address VARCHAR(45),
    resource VARCHAR(200),
    success BOOLEAN,
    details JSONB
);

CREATE INDEX IF NOT EXISTS idx_security_audit_timestamp ON security_audit_log(timestamp DESC);

-- Network traffic monitoring
CREATE TABLE IF NOT EXISTS network_traffic (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(45),
    destination_ip VARCHAR(45),
    port INTEGER,
    protocol VARCHAR(10),
    bytes_transferred BIGINT,
    connection_duration DOUBLE PRECISION,
    threat_indicators JSONB
);

CREATE INDEX IF NOT EXISTS idx_network_traffic_timestamp ON network_traffic(timestamp DESC);

-- System metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cpu_usage DOUBLE PRECISION,
    memory_usage DOUBLE PRECISION,
    disk_usage DOUBLE PRECISION,
    network_connections INTEGER,
    active_sessions INTEGER,
    failed_logins INTEGER,
    api_requests_per_minute INTEGER,
    threat_detections INTEGER
);

CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

-- ================================================
-- AI ETHICS & FAIRNESS
-- ================================================

-- AI decision audit
CREATE TABLE IF NOT EXISTS ai_decision_audit (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_name VARCHAR(100),
    input_data JSONB,
    prediction JSONB,
    confidence_score DOUBLE PRECISION,
    explanation JSONB,
    human_reviewed BOOLEAN DEFAULT false,
    ethical_flags JSONB
);

CREATE INDEX IF NOT EXISTS idx_ai_audit_timestamp ON ai_decision_audit(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ai_audit_model ON ai_decision_audit(model_name, timestamp DESC);

-- Bias detection log
CREATE TABLE IF NOT EXISTS bias_detection_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_name VARCHAR(100),
    bias_type VARCHAR(50),
    severity DOUBLE PRECISION,
    affected_groups JSONB,
    description TEXT,
    evidence JSONB,
    mitigation_applied BOOLEAN DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_bias_detection_timestamp ON bias_detection_log(timestamp DESC);

-- Fairness metrics log
CREATE TABLE IF NOT EXISTS fairness_metrics_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_name VARCHAR(100),
    metric_type VARCHAR(50),
    score DOUBLE PRECISION,
    groups_compared JSONB,
    statistical_significance BOOLEAN,
    interpretation TEXT
);

CREATE INDEX IF NOT EXISTS idx_fairness_metrics_timestamp ON fairness_metrics_log(timestamp DESC);

-- Data validation log
CREATE TABLE IF NOT EXISTS data_validation_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100),
    validation_type VARCHAR(50),
    status VARCHAR(20),
    errors_found INTEGER DEFAULT 0,
    details JSONB
);

CREATE INDEX IF NOT EXISTS idx_data_validation_timestamp ON data_validation_log(timestamp DESC);

-- Ethics reports
CREATE TABLE IF NOT EXISTS ethics_reports (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_name VARCHAR(100),
    dataset_description TEXT,
    overall_ethics_level VARCHAR(20),
    transparency_score DOUBLE PRECISION,
    explainability_score DOUBLE PRECISION,
    bias_count INTEGER DEFAULT 0,
    fairness_violations INTEGER DEFAULT 0,
    recommendations JSONB,
    full_report JSONB
);

CREATE INDEX IF NOT EXISTS idx_ethics_reports_timestamp ON ethics_reports(timestamp DESC);

-- ================================================
-- VIEWS FOR COMMON QUERIES
-- ================================================

-- View for active users with their tier and usage
CREATE OR REPLACE VIEW active_users_summary AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.tier,
    u.is_admin,
    u.last_login,
    um.api_calls,
    um.reports_generated,
    um.data_downloads
FROM users u
LEFT JOIN usage_metrics um ON u.id = um.user_id
WHERE u.is_active = true;

-- View for recent weather data by city
CREATE OR REPLACE VIEW recent_weather_by_city AS
SELECT 
    city,
    MAX(date) as latest_date,
    COUNT(*) as total_records,
    AVG(temperature) as avg_temperature,
    AVG(humidity) as avg_humidity,
    SUM(CASE WHEN rain = true THEN 1 ELSE 0 END) as rainy_days
FROM weather_data
WHERE date > CURRENT_DATE - INTERVAL '30 days'
GROUP BY city;

-- ================================================
-- FUNCTIONS
-- ================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_usage_metrics_updated_at ON usage_metrics;
CREATE TRIGGER update_usage_metrics_updated_at
    BEFORE UPDATE ON usage_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- INITIAL DATA
-- ================================================

-- Create default admin user (password should be changed immediately)
-- Default password: admin123 (hashed with bcrypt)
INSERT INTO users (username, email, hashed_password, full_name, is_admin, tier)
VALUES (
    'admin',
    'admin@gisops.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztOSDAU3kW6i',
    'System Administrator',
    true,
    'professional'
)
ON CONFLICT (username) DO NOTHING;

-- ================================================
-- DATABASE STATISTICS
-- ================================================

-- Current statistics (as of October 16, 2025):
-- - Users: Variable
-- - Weather Data Records: 52,435 (from 1997-01-31 to 2025-10-17)
-- - Cities: 5 (Colombo, Jaffna, Kandy, Matara, Trincomalee)
-- - Records per city: 10,487

-- ================================================
-- MAINTENANCE
-- ================================================

-- Create maintenance function to clean old logs
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS void AS $$
BEGIN
    -- Delete API logs older than 90 days
    DELETE FROM api_access_log WHERE timestamp < NOW() - INTERVAL '90 days';
    
    -- Delete old notifications (read and older than 30 days)
    DELETE FROM notifications WHERE read = true AND timestamp < NOW() - INTERVAL '30 days';
    
    -- Delete old auth events (older than 180 days)
    DELETE FROM auth_events WHERE timestamp < NOW() - INTERVAL '180 days';
    
    RAISE NOTICE 'Old logs cleaned up successfully';
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- BACKUP RECOMMENDATIONS
-- ================================================

-- Recommended backup schedule:
-- - Daily: pg_dump for full database backup
-- - Hourly: Continuous archiving with WAL
-- - Critical tables: users, payments, weather_data

-- Example backup command:
-- pg_dump -h localhost -U postgres -d GISDb -F c -b -v -f "GISDb_backup_$(date +%Y%m%d).backup"

-- ================================================
-- END OF SCHEMA
-- ================================================
