CREATE TABLE IF NOT EXISTS dq_runs (
    run_id UUID PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP NOT NULL,
    success BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dq_check_results (
    id BIGSERIAL PRIMARY KEY,

    run_id UUID NOT NULL,

    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(100) NOT NULL,

    status VARCHAR(20) NOT NULL,
    severity VARCHAR(20) NOT NULL,

    total_rows BIGINT,
    failed_rows BIGINT,

    expected JSONB,
    actual JSONB,

    metric VARCHAR(100),

    message TEXT,

    execution_time_ms DOUBLE PRECISION,

    CONSTRAINT fk_dq_run
        FOREIGN KEY (run_id)
        REFERENCES dq_runs(run_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dq_check_results_run_id
    ON dq_check_results(run_id);

CREATE INDEX IF NOT EXISTS idx_dq_check_results_rule_name
    ON dq_check_results(rule_name);

CREATE INDEX IF NOT EXISTS idx_dq_check_results_metric
    ON dq_check_results(metric);

CREATE INDEX IF NOT EXISTS idx_dq_runs_started_at
    ON dq_runs(started_at);