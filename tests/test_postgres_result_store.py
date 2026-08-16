from datetime import datetime
from uuid import uuid4

import psycopg2

from dq_engine.core.metrics import Metric
from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
    Severity,
)
from dq_engine.core.results import RunResult
from dq_engine.core.run import RunContext
from dq_engine.database.connection import (
    get_postgres_connection_string,
)
from dq_engine.storage.postgres import PostgresResultStore


def test_postgres_result_store_saves_run_result():

    context = RunContext.create()

    check_result = CheckResult(
        rule_name="order_id_not_null",
        rule_type="not_null",
        status=CheckStatus.FAILED,
        severity=Severity.CRITICAL,
        total_rows=5,
        failed_rows=1,
        expected=0,
        actual=1,
        metric="null_count",
        message="Found null values.",
        execution_time_ms=12.5,
    )

    run_result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[check_result],
    )

    store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    store.save(run_result)

    connection = psycopg2.connect(
        get_postgres_connection_string()
    )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                run_id,
                success
            FROM dq_runs
            WHERE run_id = %s
            """,
            (str(run_result.run_id),),
        )

        run_row = cursor.fetchone()

        assert run_row is not None
        assert str(run_row[0]) == str(run_result.run_id)
        assert run_row[1] is False

        cursor.execute(
            """
            SELECT
                rule_name,
                rule_type,
                status,
                severity,
                metric,
                total_rows,
                failed_rows
            FROM dq_check_results
            WHERE run_id = %s
            """,
            (str(run_result.run_id),),
        )

        check_row = cursor.fetchone()

        assert check_row is not None

        assert check_row[0] == "order_id_not_null"
        assert check_row[1] == "not_null"
        assert check_row[2] == "FAILED"
        assert check_row[3] == "critical"
        assert check_row[4] == "null_count"
        assert check_row[5] == 5
        assert check_row[6] == 1

    finally:
        cursor.execute(
            """
            DELETE FROM dq_check_results
            WHERE run_id = %s
            """,
            (str(run_result.run_id),),
        )

        cursor.execute(
            """
            DELETE FROM dq_runs
            WHERE run_id = %s
            """,
            (str(run_result.run_id),),
        )

        connection.commit()

        cursor.close()
        connection.close()


def test_postgres_result_store_get_run(
        valid_orders_data,
):

    context = RunContext.create()

    check_result = CheckResult(
        rule_name="order_id_not_null",
        rule_type="not_null",
        status=CheckStatus.PASSED,
        severity=Severity.CRITICAL,
        total_rows=5,
        failed_rows=0,
        expected=0,
        actual=0,
        metric="null_count",
    )

    run_result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[check_result],
    )

    store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    store.save(run_result)

    found = store.get_run(
        run_result.run_id
    )

    assert found is not None
    assert found.run_id == run_result.run_id

    assert len(found.results) == 1

    result = found.results[0]

    assert result.rule_name == "order_id_not_null"
    assert result.rule_type == "not_null"
    assert result.status == CheckStatus.PASSED
    assert result.metric == "null_count"
    assert result.actual == 0


def test_postgres_result_store_returns_none_for_unknown_run():

    store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    context = RunContext.create()

    result = store.get_run(
        context.run_id
    )

    assert result is None


def test_postgres_result_store_saves_metric():

    store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    run_id = uuid4()

    now = datetime.utcnow()

    run_result = RunResult(
        run_id=run_id,
        started_at=now,
        finished_at=now,
        results=[
            CheckResult(
                rule_name="orders_row_count",
                rule_type="row_count",
                status=CheckStatus.PASSED,
                severity=Severity.HIGH,
                total_rows=5,
                failed_rows=0,
                expected=None,
                actual=5,
                metric="row_count",
            )
        ],
    )

    store.save(run_result)

    metric = Metric(
        run_id=run_id,
        rule_name="orders_row_count",
        rule_type="row_count",
        metric_name="row_count",
        value=5.0,
        timestamp=now,
    )

    store.save_metrics([metric])


def test_postgres_result_store_saves_and_gets_anomaly(
        valid_orders_data,
):

    from datetime import datetime
    from uuid import uuid4

    from dq_engine.core.anomalies import AnomalyResult

    store = PostgresResultStore(
        get_postgres_connection_string()
    )

    run_id = uuid4()

    run_result = RunResult(
        run_id=run_id,
        started_at=datetime.utcnow(),
        finished_at=datetime.utcnow(),
        results=[],
        anomalies=[
            AnomalyResult(
                run_id=run_id,
                rule_name="orders_row_count",
                metric_name="row_count",
                actual=10.0,
                expected=5.0,
                deviation=5.0,
                score=1.0,
                is_anomaly=True,
                method="threshold",
                message="row_count exceeded threshold.",
            )
        ],
    )

    store.save(run_result)

    loaded = store.get_run(run_id)

    assert loaded is not None

    assert len(loaded.anomalies) == 1

    anomaly = loaded.anomalies[0]

    assert anomaly.rule_name == "orders_row_count"
    assert anomaly.metric_name == "row_count"
    assert anomaly.actual == 10.0
    assert anomaly.expected == 5.0
    assert anomaly.deviation == 5.0
    assert anomaly.score == 1.0
    assert anomaly.is_anomaly is True
    assert anomaly.method == "threshold"


def test_postgres_result_store_metric_history(
        valid_orders_data,
):

    from datetime import datetime
    from uuid import uuid4

    from dq_engine.core.metrics import Metric
    from dq_engine.core.results import RunResult

    store = PostgresResultStore(
        get_postgres_connection_string()
    )

    run_id = uuid4()

    run_result = RunResult(
        run_id=run_id,
        started_at=datetime.utcnow(),
        finished_at=datetime.utcnow(),
        results=[],
    )

    store.save(run_result)

    metric = Metric(
        run_id=run_id,
        rule_name="orders_row_count",
        rule_type="row_count",
        metric_name="row_count",
        value=5.0,
        timestamp=run_result.finished_at,
    )

    store.save_metrics([metric])

    history = store.get_metric_history(
        rule_name="orders_row_count",
        metric_name="row_count",
        limit=30,
    )

    assert len(history) >= 1

    assert any(
        item.run_id == run_id
        and item.rule_name == "orders_row_count"
        and item.metric_name == "row_count"
        and item.value == 5.0
        for item in history
    )