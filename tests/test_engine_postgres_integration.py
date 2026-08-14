from dq_engine.backends.postgres import PostgresBackend
from dq_engine.core.engine import DQEngine
from dq_engine.core.models import CheckStatus
from dq_engine.core.registry import RuleRegistry
from dq_engine.database.connection import (
    get_postgres_connection_string,
)


def test_engine_runs_not_null_check_on_postgres():

    registry = RuleRegistry()

    engine = DQEngine.from_config(
        "tests/fixtures/not_null.yaml",
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

    assert len(results) == 1

    result = results[0]

    assert result.rule_name == "order_id_not_null"

    assert result.rule_type == "not_null"

    assert result.status == CheckStatus.FAILED

    assert result.total_rows == 5

    assert result.failed_rows == 1

    assert result.expected == 0

    assert result.actual == 1

    assert result.execution_time_ms is not None