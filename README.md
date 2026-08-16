# Data Quality & Anomaly Detection Engine

A configurable, backend-independent Data Quality (DQ) and Anomaly Detection engine designed to run data quality checks on database tables and integrate with ETL/ELT workflows such as Apache Airflow.

The project separates **data quality rules**, **metric extraction**, **anomaly detection**, **result storage**, and **database execution** into independent layers.

---

## Overview

The engine is designed around the following flow:

```text
                 ┌─────────────────────┐
                 │     Airflow DAG     │
                 │      / Python       │
                 └──────────┬──────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │     DQEngine     │
                  └────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ConfigLoader   RuleRegistry  RunContext
              │            │
              ▼            ▼
          YAML Config    DQ Rules
                           │
                           ▼
                    ExecutionPlan
                           │
                           ▼
                    Backend Executor
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
            PostgreSQL           Vertica
              Backend             Backend
                 │                   │
                 └─────────┬─────────┘
                           ▼
                       CheckResult
                           │
                           ▼
                    MetricExtractor
                           │
                           ▼
                         Metric
                           │
                           ▼
                    AnomalyEngine
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Threshold    Percentage     Z-Score
                           │
                           ▼
                     AnomalyResult
                           │
                           ▼
                     ResultStore
                    ┌──────┴──────┐
                    ▼             ▼
                 Memory        PostgreSQL
```

---

# Features

## Data Quality Checks

The engine supports configurable checks such as:

* Not Null
* Uniqueness
* Row Count
* Accepted Values
* Range
* Additional SQL-based rules

Rules are created dynamically through the `RuleRegistry`.

Example:

```yaml
table:
  name: sales.orders

checks:

  - name: order_id_not_null
    type: not_null
    severity: critical

    column: order_id

  - name: order_id_unique
    type: unique
    severity: high

    column: order_id
```

---

# Anomaly Detection

DQ metrics can optionally be monitored for anomalies.

Supported detection methods:

### Threshold

Detects whether a metric exceeds or falls below a configured threshold.

```yaml
anomaly:
  enabled: true
  method: threshold
  threshold: 0
  direction: above
```

### Percentage Change

Compares the current metric against historical values.

```yaml
anomaly:
  enabled: true
  method: percentage_change
  threshold: 0.30
  min_history: 1
```

### Z-Score

Uses historical metric values to determine whether the current value deviates significantly from the historical distribution.

```yaml
anomaly:
  enabled: true
  method: z_score
  threshold: 3.0
  min_history: 5
```

The detection logic is isolated behind the `AnomalyDetector` abstraction, making additional algorithms possible without changing the engine.

---

# Configuration

DQ definitions are stored in YAML files.

The recommended structure is:

```text
configs/
└── vertica/
    └── <database>/
        ├── <schema_1>/
        │   ├── <table_1>.yaml
        │   └── <table_2>.yaml
        │
        └── <schema_2>/
            └── <table_3>.yaml
```

For example:

```text
configs/
└── vertica/
    └── dwh/
        ├── sales/
        │   ├── orders.yaml
        │   └── order_items.yaml
        │
        └── finance/
            └── payments.yaml
```

A table configuration contains its fully qualified table name:

```yaml
table:
  name: sales.orders
```

Database connection information is intentionally kept outside the YAML configuration. This allows the same DQ configuration to be used across different environments.

---

# Architecture

The project is divided into several layers.

```text
dq_engine/
│
├── anomaly/
├── backends/
├── config/
├── core/
├── database/
├── rules/
└── storage/
```

## Core

The `core` package contains the engine's domain objects and orchestration logic.

Important components:

* `DQEngine`
* `RunContext`
* `RunResult`
* `CheckResult`
* `Metric`
* `MetricExtractor`
* `AnomalyResult`
* `ResultStore`
* `MetricHistoryProvider`
* `ExecutionContext`

---

## Rules

Rules translate a DQ configuration into an `ExecutionPlan`.

```text
YAML
 ↓
RuleRegistry
 ↓
Rule
 ↓
ExecutionPlan
 ↓
Backend
 ↓
CheckResult
```

This allows the same rule definition to be executed by different database backends.

---

## Backends

Backends are responsible for executing generated execution plans against a data source.

Current architecture includes support for:

```text
PostgreSQL
Vertica
Python
Spark
```

The backend abstraction allows DQ rules to remain independent from the underlying execution technology.

---

# Result Model

Each engine execution creates a `RunResult`.

A run contains:

```text
RunResult
│
├── run_id
├── started_at
├── finished_at
├── success
│
└── results[]
      │
      ├── rule_name
      ├── rule_type
      ├── status
      ├── severity
      ├── total_rows
      ├── failed_rows
      ├── expected
      ├── actual
      ├── metric
      ├── message
      └── execution_time_ms
```

The engine then extracts numerical metrics from these results.

```text
CheckResult
     │
     ▼
MetricExtractor
     │
     ▼
Metric
```

A metric contains:

```text
run_id
rule_name
rule_type
metric_name
value
timestamp
```

---

# Anomaly Result

When anomaly detection is enabled, the engine produces an `AnomalyResult`.

```text
AnomalyResult
│
├── run_id
├── rule_name
├── metric_name
├── actual
├── expected
├── deviation
├── score
├── is_anomaly
├── method
└── message
```

This keeps anomaly detection separate from the original DQ result.

A DQ check can therefore pass while its metric is still considered anomalous relative to historical behavior.

---

# Result Storage

The engine uses the `ResultStore` abstraction.

Two storage implementations are available:

```text
ResultStore
├── InMemoryResultStore
└── PostgresResultStore
```

## In-Memory

Useful for:

* Unit tests
* Local development
* Lightweight execution

It stores:

```text
RunResult
Metric
AnomalyResult
```

in memory.

## PostgreSQL

The PostgreSQL result store persists:

```text
dq_runs
dq_check_results
dq_metrics
dq_anomalies
```

This provides historical data required by anomaly detection.

The database schema is located at:

```text
dq_engine/storage/sql/schema.sql
```

---

# Metric History

Historical metrics are exposed through:

```python
MetricHistoryProvider
```

The anomaly detection flow is:

```text
Current Metric
      │
      ▼
MetricHistoryProvider
      │
      ▼
Historical Metrics
      │
      ▼
AnomalyDetector
      │
      ▼
AnomalyResult
```

This abstraction allows anomaly detection to work independently of the storage implementation.

---

# Airflow Integration

The intended production usage is through Apache Airflow.

The DQ engine itself does not need to become an HTTP API.

Instead, an Airflow task can directly instantiate the engine:

```python
@task
def run_dq(
    config_path: str,
    connection_string: str,
):
    registry = RuleRegistry()

    store = PostgresResultStore(
        connection_string=connection_string,
    )

    backend = VerticaBackend(
        connection_string=connection_string,
    )

    engine = DQEngine.from_config(
        config_path,
        registry=registry,
        result_store=store,
    )

    return engine.run(
        source=None,
        backend=backend,
    )
```

The configuration path and target table can therefore be dynamic.

For example:

```text
ETL DAG
   │
   ├── Extract
   ├── Transform
   ├── Load / MERGE
   │
   ▼
DQ Task
   │
   ├── Not Null
   ├── Unique
   ├── Row Count
   ├── Accepted Values
   └── Range
   │
   ▼
Result Store
```

---

# ETL and DQ

The intended architecture keeps ETL operational metrics and DQ validation logically separate while allowing them to run in the same Airflow workflow.

For example:

```text
ETL
 │
 ├── Source row count
 ├── MERGE
 ├── Inserted rows
 ├── Updated rows
 ├── Deleted rows
 └── Total rows after
 │
 ▼
DQ Engine
 │
 ├── Null checks
 ├── Uniqueness checks
 ├── Validity checks
 ├── Range checks
 └── Other DQ rules
 │
 ▼
Result Store
```

ETL metrics describe **what happened during the load**.

DQ checks describe **whether the resulting dataset satisfies the expected quality rules**.

These concerns can therefore coexist within the same DAG without being coupled inside the DQ engine itself.

---

# Anomaly Monitoring

Anomaly detection can also be executed independently from the ETL/DQ DAG.

For example, a separate scheduled Airflow DAG can periodically evaluate historical metrics:

```text
Anomaly Monitoring DAG
        │
        ▼
Metric History
        │
        ▼
Anomaly Detector
        │
        ├── Threshold
        ├── Percentage Change
        └── Z-Score
        │
        ▼
Alert / Notification
```

This allows anomaly monitoring to run on a schedule such as every 15 minutes without requiring the original ETL DAG to execute again.

---

# Example End-to-End Flow

A typical production flow can look like:

```text
                  Airflow
                     │
                     ▼
              ETL DAG starts
                     │
                     ▼
              Extract from DB
                     │
                     ▼
              Spark processing
                     │
                     ▼
              Vertica MERGE
                     │
                     ▼
            ETL metrics/logging
                     │
                     ▼
                DQ Engine
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Not Null    Unique    Row Count
          │          │          │
          └──────────┼──────────┘
                     ▼
                 Metrics
                     │
                     ▼
               Result Store
```

Then independently:

```text
          Every 15 minutes
                 │
                 ▼
        Anomaly Monitoring DAG
                 │
                 ▼
          Historical Metrics
                 │
                 ▼
         Anomaly Detection
                 │
                 ▼
              Alert
```

---

# Testing

The project uses `pytest`.

Tests cover:

```text
tests/
├── test_engine.py
├── test_engine_anomaly.py
├── test_anomaly_engine.py
├── test_anomaly_factory.py
├── test_threshold_detector.py
├── test_percentage_detector.py
├── test_zscore_detector.py
├── test_metric_extractor.py
├── test_metric_history.py
├── test_result_store.py
├── test_postgres_result_store.py
├── test_postgres_backend.py
├── test_postgres_backend_integration.py
├── test_engine_postgres_basic.py
├── test_engine_postgres_integration.py
├── test_rules.py
├── test_config.py
└── ...
```

Run the test suite with:

```bash
pytest
```

Integration tests require the corresponding database environment to be available.

---

# Project Structure

```text
dq_platform/
│
├── configs/
│   ├── examples/
│   └── vertica/
│
├── dq_engine/
│   ├── anomaly/
│   │   ├── base.py
│   │   ├── engine.py
│   │   ├── factory.py
│   │   ├── percentage.py
│   │   ├── threshold.py
│   │   └── zscore.py
│   │
│   ├── backends/
│   │   ├── base.py
│   │   ├── postgres.py
│   │   ├── python.py
│   │   ├── spark.py
│   │   └── vertica.py
│   │
│   ├── config/
│   │   ├── loader.py
│   │   └── schema.py
│   │
│   ├── core/
│   │   ├── anomalies.py
│   │   ├── context.py
│   │   ├── engine.py
│   │   ├── executor.py
│   │   ├── metric_extractor.py
│   │   ├── metric_history.py
│   │   ├── metrics.py
│   │   ├── models.py
│   │   ├── registry.py
│   │   ├── result_store.py
│   │   ├── results.py
│   │   └── run.py
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   ├── rules/
│   │   ├── base.py
│   │   ├── completeness.py
│   │   ├── sql.py
│   │   ├── uniqueness.py
│   │   ├── validity.py
│   │   └── volume.py
│   │
│   └── storage/
│       ├── memory.py
│       ├── postgres.py
│       └── sql/
│           └── schema.sql
│
├── dags/
│
└── tests/
```

---

# Design Principles

The project follows several core principles:

### Separation of Concerns

DQ rules, execution, metrics, anomaly detection, storage, and orchestration are separated.

### Configuration Driven

Rules and anomaly behavior are defined through YAML rather than hard-coded into DAGs.

### Backend Independent

The same rule system can generate execution plans for different backends.

### Storage Independent

The engine can operate with in-memory storage for tests or PostgreSQL for persistent history.

### Airflow Friendly

The engine is designed to be called directly from Airflow Python tasks rather than requiring an additional API layer.

### Extensible

New:

* DQ rules
* database backends
* anomaly detectors
* result stores

can be added behind existing abstractions.

---

# Current Status

The core DQ and anomaly detection layers are implemented and covered by tests.

Current capabilities include:

* Config-driven DQ rules
* Rule registry
* Execution plans
* PostgreSQL backend
* Result persistence
* Metric extraction
* Metric history
* Threshold anomaly detection
* Percentage-change anomaly detection
* Z-score anomaly detection
* Anomaly result persistence
* In-memory result store
* PostgreSQL result store
* Airflow-oriented execution architecture

The next integration layer is the **Vertica backend and Airflow DAG integration**.
