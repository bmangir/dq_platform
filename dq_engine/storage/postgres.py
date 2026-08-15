import json

import psycopg2

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
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
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

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()