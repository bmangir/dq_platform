from dq_engine.backends.postgres import PostgresBackend
from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import (
    CheckStatus,
    ExecutionPlan,
    Severity,
)
from dq_engine.database.connection import (
    get_postgres_connection_string,
)


def test_postgres_backend_executes_count_nulls():

    backend = PostgresBackend(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    plan = ExecutionPlan(
        rule_name="order_id_not_null",
        rule_type="not_null",
        severity=Severity.CRITICAL,
        operation="count_nulls",
        parameters={
            "column": "order_id",
        },
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    result = backend.execute(
        plan=plan,
        context=context,
    )

    assert result.status == CheckStatus.FAILED

    assert result.total_rows == 5

    assert result.failed_rows == 1

    assert result.expected == 0

    assert result.actual == 1


def test_postgres_backend_executes_unique():

    backend = PostgresBackend(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    plan = ExecutionPlan(
        rule_name="order_id_unique",
        rule_type="unique",
        severity=Severity.HIGH,
        operation="unique",
        parameters={
            "column": "order_id",
        },
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    result = backend.execute(
        plan=plan,
        context=context,
    )

    assert result.status == CheckStatus.FAILED

    assert result.total_rows == 5

    assert result.failed_rows == 1

    assert result.expected == 0

    assert result.actual == 1