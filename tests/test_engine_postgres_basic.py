from dq_engine.backends.postgres import PostgresBackend
from dq_engine.core.engine import DQEngine
from dq_engine.core.models import CheckStatus
from dq_engine.core.registry import RuleRegistry
from dq_engine.database.connection import (
    get_postgres_connection_string,
)


def test_engine_runs_basic_dq_checks_on_postgres():

    registry = RuleRegistry()

    engine = DQEngine.from_config(
        "tests/fixtures/orders_basic.yaml",
        registry=registry,
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

    assert len(results) == 2

    not_null_result = results[0]

    assert (
            not_null_result.rule_name
            == "order_id_not_null"
    )

    assert (
            not_null_result.status
            == CheckStatus.FAILED
    )

    assert not_null_result.total_rows == 5
    assert not_null_result.failed_rows == 1

    row_count_result = results[1]

    assert (
            row_count_result.rule_name
            == "orders_row_count"
    )

    assert (
            row_count_result.status
            == CheckStatus.PASSED
    )

    assert row_count_result.total_rows == 5
    assert row_count_result.actual == 5