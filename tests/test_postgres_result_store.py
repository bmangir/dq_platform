import psycopg2

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