-- ============================================================
-- DQ Engine - Vertica Storage Schema
-- ============================================================

-- Schema
-- CREATE SCHEMA IF NOT EXISTS dq_platform;


-- ============================================================
-- DQ RUNS
-- ============================================================

CREATE TABLE IF NOT EXISTS dq_platform.dq_runs (
    run_id UUID NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP NOT NULL,
    success BOOLEAN NOT NULL
);


-- ============================================================
-- DQ CHECK RESULTS
-- ============================================================

CREATE TABLE IF NOT EXISTS dq_platform.dq_check_results (
    id IDENTITY,
    run_id UUID NOT NULL,

    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(100) NOT NULL,

    status VARCHAR(20) NOT NULL,
    severity VARCHAR(20) NOT NULL,

    total_rows INTEGER,
    failed_rows INTEGER,

    expected LONG VARCHAR,
    actual LONG VARCHAR,

    metric VARCHAR(255),
    message LONG VARCHAR,

    execution_time_ms FLOAT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- DQ METRICS
-- ============================================================

CREATE TABLE IF NOT EXISTS dq_platform.dq_metrics (
    id IDENTITY,

    run_id UUID NOT NULL,

    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(100) NOT NULL,

    metric_name VARCHAR(255) NOT NULL,
    value FLOAT NOT NULL,

    timestamp TIMESTAMP NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- DQ ANOMALIES
-- ============================================================

CREATE TABLE IF NOT EXISTS dq_platform.dq_anomalies (
    id IDENTITY,

    run_id UUID NOT NULL,

    rule_name VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,

    actual FLOAT NOT NULL,
    expected FLOAT NOT NULL,

    deviation FLOAT NOT NULL,
    score FLOAT NOT NULL,

    is_anomaly BOOLEAN NOT NULL,

    method VARCHAR(100) NOT NULL,
    message LONG VARCHAR,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- PROJECTIONS
-- ============================================================

-- DQ Runs
CREATE PROJECTION IF NOT EXISTS dq_platform.dq_runs_projection
AS
SELECT
    run_id,
    started_at,
    finished_at,
    success
FROM dq_platform.dq_runs
ORDER BY started_at, run_id
SEGMENTED BY HASH(run_id) ALL NODES;


-- DQ Check Results
CREATE PROJECTION IF NOT EXISTS dq_platform.dq_check_results_projection
AS
SELECT
    id,
    run_id,
    rule_name,
    rule_type,
    status,
    severity,
    total_rows,
    failed_rows,
    expected,
    actual,
    metric,
    message,
    execution_time_ms,
    created_at
FROM dq_platform.dq_check_results
ORDER BY run_id, rule_name, id
SEGMENTED BY HASH(run_id) ALL NODES;


-- DQ Metrics
CREATE PROJECTION IF NOT EXISTS dq_platform.dq_metrics_projection
AS
SELECT
    id,
    run_id,
    rule_name,
    rule_type,
    metric_name,
    value,
    timestamp,
    created_at
FROM dq_platform.dq_metrics
ORDER BY rule_name, metric_name, timestamp, id
SEGMENTED BY HASH(rule_name, metric_name) ALL NODES;


-- DQ Anomalies
CREATE PROJECTION IF NOT EXISTS dq_platform.dq_anomalies_projection
AS
SELECT
    id,
    run_id,
    rule_name,
    metric_name,
    actual,
    expected,
    deviation,
    score,
    is_anomaly,
    method,
    message,
    created_at
FROM dq_platform.dq_anomalies
ORDER BY rule_name, metric_name, id
SEGMENTED BY HASH(rule_name, metric_name) ALL NODES;