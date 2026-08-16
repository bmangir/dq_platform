import time

import vertica_python

from dq_engine.backends.base import BaseBackend
from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
    ExecutionPlan,
)


class VerticaBackend(BaseBackend):

    def __init__(
            self,
            connection_info: dict,
    ):
        self.connection_info = connection_info

        self._executors = {
            "count_nulls": self._count_nulls,
            "row_count": self._row_count,
            "unique": self._unique,
            "accepted_values": self._accepted_values,
            "range": self._range,
        }

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
                total_rows=result.get("total_rows"),
                failed_rows=result.get("failed_rows"),
                expected=result.get("expected"),
                actual=result.get("actual"),
                metric=result.get("metric"),
                message=result.get("message"),
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

    def _execute_query(
            self,
            query: str,
            parameters=None,
    ):

        with vertica_python.connect(
                **self.connection_info
        ) as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    parameters,
                )

                return cursor.fetchone()

    def _execute_plan(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> dict:

        executor = self._executors.get(
            plan.operation
        )

        if executor is None:
            raise ValueError(
                f"Unsupported operation: "
                f"{plan.operation}"
            )

        return executor(
            plan=plan,
            context=context,
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

        total_rows, failed_rows = (
            self._execute_query(query)
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
            "metric": "null_count",
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

    def _row_count(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> dict:

        query = self._build_row_count_query(
            context=context,
        )

        row = self._execute_query(query)

        actual = row[0]

        min_rows = plan.parameters.get("min")
        max_rows = plan.parameters.get("max")

        passed = True

        if min_rows is not None:
            passed = passed and actual >= min_rows

        if max_rows is not None:
            passed = passed and actual <= max_rows

        status = (
            CheckStatus.PASSED
            if passed
            else CheckStatus.FAILED
        )

        return {
            "status": status,
            "total_rows": actual,
            "failed_rows": 0 if passed else 1,
            "expected": {
                "min": min_rows,
                "max": max_rows,
            },
            "actual": actual,
            "metric": "row_count",
            "message": (
                "Row count is within the expected range."
                if passed
                else (
                    f"Row count {actual} is outside "
                    f"the expected range "
                    f"[{min_rows}, {max_rows}]."
                )
            ),
        }

    def _build_row_count_query(
            self,
            context: ExecutionContext,
    ) -> str:

        table = context.table

        return f"""
            SELECT COUNT(*)
            FROM {table}
        """

    def _build_unique_query(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> str:

        column = plan.parameters["column"]
        table = context.table

        return f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT("{column}") AS non_null_rows,
                COUNT(DISTINCT "{column}") AS distinct_rows
            FROM {table}
        """

    def _unique(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> dict:

        query = self._build_unique_query(
            plan=plan,
            context=context,
        )

        (
            total_rows,
            non_null_rows,
            distinct_rows,
        ) = self._execute_query(query)

        duplicate_rows = (
                non_null_rows - distinct_rows
        )

        status = (
            CheckStatus.PASSED
            if duplicate_rows == 0
            else CheckStatus.FAILED
        )

        return {
            "status": status,
            "total_rows": total_rows,
            "failed_rows": duplicate_rows,
            "expected": 0,
            "actual": duplicate_rows,
            "metric": "duplicate_count",
            "message": (
                "All non-null values are unique."
                if duplicate_rows == 0
                else (
                    f"{duplicate_rows} duplicate "
                    "value(s) found."
                )
            ),
        }

    def _build_accepted_values_query(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> tuple[str, list]:

        column = plan.parameters["column"]
        values = plan.parameters["values"]

        placeholders = ", ".join(
            ["%s"] * len(values)
        )

        query = f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(*) FILTER (
                    WHERE "{column}" IS NOT NULL
                      AND "{column}" NOT IN ({placeholders})
                ) AS failed_rows
            FROM {context.table}
        """

        return query, values

    def _accepted_values(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> dict:

        query, parameters = (
            self._build_accepted_values_query(
                plan=plan,
                context=context,
            )
        )

        total_rows, failed_rows = (
            self._execute_query(
                query,
                parameters,
            )
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
            "expected": plan.parameters["values"],
            "actual": failed_rows,
            "metric": "invalid_value_count",
            "message": (
                "All values are accepted."
                if failed_rows == 0
                else (
                    f"{failed_rows} invalid "
                    "value(s) found."
                )
            ),
        }

    def _build_range_query(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> tuple[str, list]:

        column = plan.parameters["column"]
        minimum = plan.parameters["min"]
        maximum = plan.parameters["max"]

        conditions = []
        parameters = []

        if minimum is not None:
            conditions.append(
                f'"{column}" < %s'
            )
            parameters.append(minimum)

        if maximum is not None:
            conditions.append(
                f'"{column}" > %s'
            )
            parameters.append(maximum)

        invalid_condition = " OR ".join(
            conditions
        )

        query = f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(*) FILTER (
                    WHERE "{column}" IS NOT NULL
                      AND ({invalid_condition})
                ) AS failed_rows
            FROM {context.table}
        """

        return query, parameters

    def _range(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> dict:

        query, parameters = (
            self._build_range_query(
                plan=plan,
                context=context,
            )
        )

        total_rows, failed_rows = (
            self._execute_query(
                query,
                parameters,
            )
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
            "metric": "out_of_range_count",
            "expected": {
                "min": plan.parameters["min"],
                "max": plan.parameters["max"],
            },
            "actual": failed_rows,
            "message": (
                "All values are within range."
                if failed_rows == 0
                else (
                    f"{failed_rows} out-of-range "
                    "value(s) found."
                )
            ),
        }