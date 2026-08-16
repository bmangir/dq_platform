from dq_engine.backends.postgres import PostgresBackend
from dq_engine.core.engine import DQEngine
from dq_engine.core.models import CheckStatus
from dq_engine.core.registry import RuleRegistry
from dq_engine.database.connection import (
    get_postgres_connection_string,
)
from dq_engine.storage.postgres import (
    PostgresResultStore,
)


def test_engine_runs_basic_dq_checks_on_postgres(
        valid_orders_data,
):

    registry = RuleRegistry()
    result_store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    engine = DQEngine.from_config(
        "tests/fixtures/orders_basic.yaml",
        registry=registry,
        result_store=result_store,
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

    assert len(results.results) == 3

    results_by_name = {
        result.rule_name: result
        for result in results.results
    }

    not_null_result = results_by_name[
        "order_id_not_null"
    ]

    assert (
            not_null_result.status
            == CheckStatus.FAILED
    )

    assert not_null_result.metric == "null_count"
    assert not_null_result.total_rows == 5
    assert not_null_result.failed_rows == 1

    row_count_result = results_by_name[
        "orders_row_count"
    ]

    assert (
            row_count_result.status
            == CheckStatus.PASSED
    )

    assert row_count_result.metric == "row_count"
    assert row_count_result.total_rows == 5
    assert row_count_result.actual == 5

    unique_result = results_by_name[
        "order_id_unique"
    ]

    assert (
            unique_result.status
            == CheckStatus.PASSED
    )

    assert unique_result.metric == "duplicate_count"
    assert unique_result.total_rows == 5
    assert unique_result.failed_rows == 0
    assert unique_result.actual == 0

    assert results.run_id is not None
    assert results.started_at is not None
    assert results.finished_at is not None
    assert results.success is False


def test_engine_runs_accepted_values_on_postgres(
        invalid_order_status_data,
):

    registry = RuleRegistry()
    result_store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    engine = DQEngine.from_config(
        "tests/fixtures/orders_validity.yaml",
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

    assert result.rule_name == "order_status_valid"
    assert result.rule_type == "accepted_values"

    assert result.status == CheckStatus.FAILED

    assert result.metric == "invalid_value_count"

    assert result.total_rows == 5
    assert result.failed_rows == 1
    assert result.actual == 1

    assert result.expected == [
        "completed",
        "pending",
        "cancelled",
    ]

    assert result.execution_time_ms is not None


def test_engine_accepts_valid_values_on_postgres(
        valid_orders_data,
):

    registry = RuleRegistry()
    result_store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    engine = DQEngine.from_config(
        "tests/fixtures/orders_validity.yaml",
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

    assert result.rule_name == "order_status_valid"
    assert result.rule_type == "accepted_values"

    assert result.status == CheckStatus.PASSED

    assert result.metric == "invalid_value_count"

    assert result.total_rows == 5
    assert result.failed_rows == 0
    assert result.actual == 0

    assert result.expected == [
        "completed",
        "pending",
        "cancelled",
    ]

    assert result.execution_time_ms is not None
    assert results.success is True


def test_engine_runs_range_on_postgres(
        invalid_order_amount_data,
):

    registry = RuleRegistry()
    result_store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    engine = DQEngine.from_config(
        "tests/fixtures/orders_range.yaml",
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

    assert result.rule_name == (
        "order_amount_valid_range"
    )

    assert result.rule_type == "range"

    assert result.status == CheckStatus.FAILED

    assert result.metric == "out_of_range_count"

    assert result.total_rows == 5
    assert result.failed_rows == 1
    assert result.actual == 1

    assert result.expected == {
        "min": 0,
        "max": 10000,
    }

    assert result.execution_time_ms is not None


def test_engine_accepts_valid_range_on_postgres(
        valid_orders_data,
):

    registry = RuleRegistry()
    result_store = PostgresResultStore(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    engine = DQEngine.from_config(
        "tests/fixtures/orders_range.yaml",
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

    assert result.rule_name == (
        "order_amount_valid_range"
    )

    assert result.rule_type == "range"

    assert result.status == CheckStatus.PASSED

    assert result.metric == "out_of_range_count"

    assert result.total_rows == 5
    assert result.failed_rows == 0
    assert result.actual == 0

    assert result.expected == {
        "min": 0,
        "max": 10000,
    }

    assert result.execution_time_ms is not None