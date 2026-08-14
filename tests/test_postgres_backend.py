from dq_engine.backends.postgres import PostgresBackend
from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import (
    ExecutionPlan,
    Severity,
)


def test_postgres_backend_builds_count_nulls_query():

    backend = PostgresBackend(
        connection_string="postgresql://dummy"
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

    query = backend._build_count_nulls_query(
        plan=plan,
        context=context,
    )

    assert 'FROM public.orders' in query

    assert '"order_id" IS NULL' in query

    assert "COUNT(*) AS total_rows" in query

    assert "failed_rows" in query


def test_postgres_backend_builds_expected_count_nulls_query():

    backend = PostgresBackend(
        connection_string="postgresql://dummy"
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

    query = backend._build_count_nulls_query(
        plan=plan,
        context=context,
    )

    normalized_query = " ".join(
        query.split()
    )

    assert "SELECT COUNT(*) AS total_rows" in normalized_query

    assert (
            'COUNT(*) FILTER ( WHERE "order_id" IS NULL )'
            in normalized_query
    )

    assert "AS failed_rows" in normalized_query

    assert "FROM public.orders" in normalized_query