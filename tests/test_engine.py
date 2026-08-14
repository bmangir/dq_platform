from dq_engine.core.engine import DQEngine
from dq_engine.core.registry import RuleRegistry
from fixtures.mock_backend import MockBackend



def test_engine_runs_not_null_rule():

    registry = RuleRegistry()

    engine = DQEngine.from_config(
        "tests/fixtures/not_null.yaml",
        registry=registry,
    )

    backend = MockBackend()

    results = engine.run(
        source=None,
        backend=backend,
    )

    assert len(results) == 1

    result = results[0]

    assert result.rule_name == "order_id_not_null"
    assert result.rule_type == "not_null"

    assert result.status.value == "PASSED"

    assert result.total_rows == 100
    assert result.failed_rows == 0

    assert result.expected == 0
    assert result.actual == 0