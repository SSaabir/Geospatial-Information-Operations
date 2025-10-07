CREATE TABLE ai_decision_audit (
    id INTEGER NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    model_name VARCHAR(100),
    input_data JSONB,
    prediction JSONB,
    confidence_score FLOAT,
    explanation JSONB,
    human_reviewed BOOLEAN,
    ethical_flags JSONB
);

CREATE TABLE air_quality_data (
    id INTEGER NOT NULL PRIMARY KEY,
    country TEXT,
    statedistrict TEXT,
    datetime DATE,
    pm10 FLOAT,
    pm2_5 FLOAT,
    carbon_monoxide FLOAT,
    ozone FLOAT,
    lat FLOAT,
    lon FLOAT,
    source TEXT
);

CREATE TABLE api_access_log (
    id INTEGER NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    endpoint VARCHAR(200),
    method VARCHAR(10),
    user_id VARCHAR(50),
    ip_address VARCHAR(45),
    user_agent TEXT,
    response_code INTEGER,
    response_time FLOAT,
    request_size INTEGER,
    response_size INTEGER,
    threat_score FLOAT
);

CREATE TABLE auth_events (
    id INTEGER NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    event_type VARCHAR(50),
    user_id VARCHAR(50),
    ip_address VARCHAR(45),
    success BOOLEAN,
    failure_reason VARCHAR(200),
    session_id VARCHAR(100),
    user_agent TEXT,
    geolocation JSONB
);

CREATE TABLE bias_detection_log (
    id INTEGER NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    model_name VARCHAR(100),
    bias_type VARCHAR(50),
    severity FLOAT,
    affected_groups JSONB,
    description TEXT,
    evidence JSONB,
    mitigation_applied BOOLEAN
);

CREATE TABLE checkout_sessions (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    plan VARCHAR(50) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    recurring BOOLEAN,
    created_at TIMESTAMP,
    paid BOOLEAN,
    paid_at TIMESTAMP,
    last4 VARCHAR(4)
);

CREATE TABLE data_validation_log (
    id INTEGER NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    data_source VARCHAR(100),
    validation_type VARCHAR(50),
    status VARCHAR(20),
    errors_found INTEGER,
    details JSONB
);

CREATE TABLE ethics_reports (
    id VARCHAR(50) NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    model_name VARCHAR(100),
    dataset_description TEXT,
    overall_ethics_level VARCHAR(20),
    transparency_score FLOAT,
    explainability_score FLOAT,
    bias_count INTEGER,
    fairness_violations INTEGER,
    recommendations JSONB,
    full_report JSONB
);

CREATE TABLE fairness_metrics_log (
    id INTEGER NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    model_name VARCHAR(100),
    metric_type VARCHAR(50),
    score FLOAT,
    groups_compared JSONB,
    statistical_significance BOOLEAN,
    interpretation TEXT
);

CREATE TABLE network_traffic (
    id INTEGER NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    source_ip VARCHAR(45),
    destination_ip VARCHAR(45),
    port INTEGER,
    protocol VARCHAR(10),
    bytes_transferred INTEGER,
    connection_duration FLOAT,
    threat_indicators JSONB
);

CREATE TABLE payments (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    plan VARCHAR(50) NOT NULL,
    created_at TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    recurring BOOLEAN
);

CREATE TABLE security_alerts (
    id VARCHAR(50) NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
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

CREATE TABLE security_audit_log (
    id INTEGER NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    action VARCHAR(100),
    user_id VARCHAR(50),
    ip_address VARCHAR(45),
    resource VARCHAR(200),
    success BOOLEAN,
    details JSONB
);

CREATE TABLE security_incidents (
    id VARCHAR(50) NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    category VARCHAR(50),
    threat_level VARCHAR(20),
    title VARCHAR(200),
    description TEXT,
    source_ip VARCHAR(45),
    user_id VARCHAR(50),
    affected_resources JSONB,
    indicators JSONB,
    response_actions JSONB,
    status VARCHAR(20),
    assigned_to VARCHAR(50),
    resolution_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE system_metrics (
    id INTEGER NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_usage FLOAT,
    network_connections INTEGER,
    active_sessions INTEGER,
    failed_logins INTEGER,
    api_requests_per_minute INTEGER,
    threat_detections INTEGER
);

CREATE TABLE usage_metrics (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    api_calls INTEGER NOT NULL,
    reports_generated INTEGER NOT NULL,
    data_downloads INTEGER NOT NULL,
    updated_at TIMESTAMP
);

CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN,
    is_admin BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_login TIMESTAMP,
    avatar_url TEXT,
    tier VARCHAR(20)
);

CREATE TABLE weather_data (
    id INTEGER NOT NULL PRIMARY KEY,
    country TEXT,
    statedistrict TEXT,
    datetime DATE,
    tempmax FLOAT,
    tempmin FLOAT,
    temp FLOAT,
    humidity FLOAT,
    rain BOOLEAN,
    rainsum FLOAT,
    snow BOOLEAN,
    snowdepth FLOAT,
    windgust FLOAT,
    windspeed FLOAT,
    winddir FLOAT,
    sealevelpressure FLOAT,
    cloudcover FLOAT,
    visibility FLOAT,
    solarradiation FLOAT,
    solarenergy FLOAT,
    uvindex FLOAT,
    sunrise TIME,
    sunset TIME,
    moonphase FLOAT,
    conditions TEXT,
    description TEXT,
    icon TEXT
);

