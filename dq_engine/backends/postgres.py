import time

import psycopg2

from dq_engine.backends.base import BaseBackend
from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
    ExecutionPlan,
)


class PostgresBackend(BaseBackend):

    def __init__(
            self,
            connection_string: str,
    ):
        self.connection_string = connection_string

    def execute(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> CheckResult:

        start_time = time.perf_counter()

        try:
            result = self._execute_plan(
                plan=plan,
                context=context,
            )

            execution_time_ms = (
                                        time.perf_counter() - start_time
                                ) * 1000

            return CheckResult(
                rule_name=plan.rule_name,
                rule_type=plan.rule_type,
                status=result["status"],
                severity=plan.severity,
                total_rows=result["total_rows"],
                failed_rows=result["failed_rows"],
                expected=result["expected"],
                actual=result["actual"],
                message=result["message"],
                execution_time_ms=execution_time_ms,
            )

        except Exception as exc:

            execution_time_ms = (
                                        time.perf_counter() - start_time
                                ) * 1000

            return CheckResult(
                rule_name=plan.rule_name,
                rule_type=plan.rule_type,
                status=CheckStatus.ERROR,
                severity=plan.severity,
                message=str(exc),
                execution_time_ms=execution_time_ms,
            )

    def _execute_plan(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> dict:

        if plan.operation == "count_nulls":
            return self._count_nulls(
                plan=plan,
                context=context,
            )

        raise ValueError(
            f"Unsupported operation: {plan.operation}"
        )

    def _count_nulls(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> dict:

        query = self._build_count_nulls_query(
            plan=plan,
            context=context,
        )

        with psycopg2.connect(
                self.connection_string
        ) as connection:

            with connection.cursor() as cursor:

                cursor.execute(query)

                total_rows, failed_rows = (
                    cursor.fetchone()
                )

        status = (
            CheckStatus.PASSED
            if failed_rows == 0
            else CheckStatus.FAILED
        )

        return {
            "status": status,
            "total_rows": total_rows,
            "failed_rows": failed_rows,
            "expected": 0,
            "actual": failed_rows,
            "message": (
                "No NULL values found."
                if failed_rows == 0
                else f"{failed_rows} NULL values found."
            ),
        }

    def _build_count_nulls_query(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> str:

        column = plan.parameters["column"]
        table = context.table

        return f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(*) FILTER (
                    WHERE "{column}" IS NULL
                ) AS failed_rows
            FROM {table}
        """