from dq_engine.backends.postgres import PostgresBackend
from dq_engine.core.context import ExecutionContext
from dq_engine.core.engine import DQEngine
from dq_engine.core.models import CheckStatus, ExecutionPlan, Severity
from dq_engine.core.registry import RuleRegistry
from dq_engine.database.connection import (
    get_postgres_connection_string,
)
from dq_engine.storage.postgres import (
    PostgresResultStore,
)


def test_engine_runs_not_null_check_on_postgres():

    registry = RuleRegistry()
    result_store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    engine = DQEngine.from_config(
        "tests/fixtures/not_null.yaml",
        registry=registry,
        result_store=result_store
    )

    backend = PostgresBackend(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    results = engine.run(
        source=None,
        backend=backend,
    )

    assert len(results.results) == 1

    result = results.results[0]

    assert result.rule_name == "order_id_not_null"

    assert result.rule_type == "not_null"

    assert result.metric == "null_count"

    assert result.status == CheckStatus.FAILED

    assert result.total_rows == 5

    assert result.failed_rows == 1

    assert result.expected == 0

    assert result.actual == 1

    assert result.execution_time_ms is not None


def test_postgres_backend_executes_accepted_values(
        invalid_order_status_data,
):

    connection_string = (
        get_postgres_connection_string()
    )

    backend = PostgresBackend(
        connection_string=connection_string
    )

    plan = ExecutionPlan(
        rule_name="order_status_valid",
        rule_type="accepted_values",
        severity=Severity.HIGH,
        operation="accepted_values",
        parameters={
            "column": "order_status",
            "values": [
                "completed",
                "pending",
                "cancelled",
            ],
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
    assert result.actual == 1