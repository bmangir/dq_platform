import json
from uuid import UUID

import psycopg2

from dq_engine.core.anomalies import AnomalyResult
from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
    Severity,
)
from dq_engine.core.metrics import Metric
from dq_engine.core.result_store import ResultStore
from dq_engine.core.results import RunResult


class PostgresResultStore(ResultStore):

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def save(self, run_result: RunResult) -> None:

        connection = psycopg2.connect(
            self.connection_string
        )

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO dq_runs (
                    run_id,
                    started_at,
                    finished_at,
                    success
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    str(run_result.run_id),
                    run_result.started_at,
                    run_result.finished_at,
                    run_result.success,
                ),
            )

            for result in run_result.results:

                cursor.execute(
                    """
                    INSERT INTO dq_check_results (
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
                        execution_time_ms
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        str(run_result.run_id),
                        result.rule_name,
                        result.rule_type,
                        result.status.value,
                        result.severity.value,
                        result.total_rows,
                        result.failed_rows,
                        json.dumps(result.expected),
                        json.dumps(result.actual),
                        result.metric,
                        result.message,
                        result.execution_time_ms,
                    ),
                )

            for anomaly in run_result.anomalies:

                cursor.execute(
                    """
                    INSERT INTO dq_anomalies (
                        run_id,
                        rule_name,
                        metric_name,
                        actual,
                        expected,
                        deviation,
                        score,
                        is_anomaly,
                        method,
                        message
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        str(run_result.run_id),
                        anomaly.rule_name,
                        anomaly.metric_name,
                        anomaly.actual,
                        anomaly.expected,
                        anomaly.deviation,
                        anomaly.score,
                        anomaly.is_anomaly,
                        anomaly.method,
                        anomaly.message,
                    ),
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_run(
            self,
            run_id: UUID,
    ) -> RunResult | None:

        connection = psycopg2.connect(
            self.connection_string
        )

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    run_id,
                    started_at,
                    finished_at,
                    success
                FROM dq_runs
                WHERE run_id = %s
                """,
                (str(run_id),),
            )

            run_row = cursor.fetchone()

            if run_row is None:
                return None

            cursor.execute(
                """
                SELECT
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
                    execution_time_ms
                FROM dq_check_results
                WHERE run_id = %s
                ORDER BY id
                """,
                (str(run_id),),
            )

            check_rows = cursor.fetchall()

            results = []

            for row in check_rows:

                results.append(
                    CheckResult(
                        rule_name=row[0],
                        rule_type=row[1],
                        status=CheckStatus(row[2]),
                        severity=Severity(row[3]),
                        total_rows=row[4],
                        failed_rows=row[5],
                        expected=row[6],
                        actual=row[7],
                        metric=row[8],
                        message=row[9],
                        execution_time_ms=row[10],
                    )
                )

            cursor.execute(
                """
                SELECT
                    rule_name,
                    metric_name,
                    actual,
                    expected,
                    deviation,
                    score,
                    is_anomaly,
                    method,
                    message
                FROM dq_anomalies
                WHERE run_id = %s
                ORDER BY id
                """,
                (str(run_id),),
            )

            anomaly_rows = cursor.fetchall()

            anomalies = []

            for row in anomaly_rows:

                anomalies.append(
                    AnomalyResult(
                        run_id=UUID(str(run_id)),
                        rule_name=row[0],
                        metric_name=row[1],
                        actual=float(row[2]),
                        expected=float(row[3]),
                        deviation=float(row[4]),
                        score=float(row[5]),
                        is_anomaly=row[6],
                        method=row[7],
                        message=row[8],
                    )
                )

            return RunResult(
                run_id=UUID(str(run_row[0])),
                started_at=run_row[1],
                finished_at=run_row[2],
                results=results,
                anomalies=anomalies,
            )

        finally:
            cursor.close()
            connection.close()

    def get_history(
            self,
            rule_name: str,
            limit: int = 30,
    ) -> list[RunResult]:

        connection = psycopg2.connect(
            self.connection_string
        )

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT DISTINCT
                    r.run_id
                FROM dq_runs r
                INNER JOIN dq_check_results c
                    ON r.run_id = c.run_id
                WHERE c.rule_name = %s
                ORDER BY r.started_at DESC
                LIMIT %s
                """,
                (
                    rule_name,
                    limit,
                ),
            )

            run_ids = [
                UUID(str(row[0]))
                for row in cursor.fetchall()
            ]

        finally:
            cursor.close()
            connection.close()

        history = []

        for run_id in run_ids:

            run_result = self.get_run(run_id)

            if run_result is not None:
                history.append(run_result)

        return history

    def save_metrics(
            self,
            metrics: list[Metric],
    ) -> None:

        if not metrics:
            return

        connection = psycopg2.connect(
            self.connection_string
        )

        try:
            cursor = connection.cursor()

            for metric in metrics:

                cursor.execute(
                    """
                    INSERT INTO dq_metrics (
                        run_id,
                        rule_name,
                        rule_type,
                        metric_name,
                        value,
                        timestamp
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        str(metric.run_id),
                        metric.rule_name,
                        metric.rule_type,
                        metric.metric_name,
                        metric.value,
                        metric.timestamp,
                    ),
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_metric_history(
            self,
            rule_name: str,
            metric_name: str,
            limit: int = 30,
    ) -> list[Metric]:

        connection = psycopg2.connect(
            self.connection_string
        )

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    run_id,
                    rule_name,
                    rule_type,
                    metric_name,
                    value,
                    timestamp
                FROM dq_metrics
                WHERE rule_name = %s
                  AND metric_name = %s
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (
                    rule_name,
                    metric_name,
                    limit,
                ),
            )

            rows = cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

        return [
            Metric(
                run_id=UUID(str(row[0])),
                rule_name=row[1],
                rule_type=row[2],
                metric_name=row[3],
                value=float(row[4]),
                timestamp=row[5],
            )
            for row in rows
        ]