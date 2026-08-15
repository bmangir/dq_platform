from dq_engine.core.executor import DQExecutor
from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
    Severity,
)
from dq_engine.storage.memory import (
    InMemoryResultStore,
)


class FakeEngine:

    def run(self, source, backend):

        return [
            CheckResult(
                rule_name="order_id_not_null",
                rule_type="not_null",
                status=CheckStatus.PASSED,
                severity=Severity.CRITICAL,
                total_rows=5,
                failed_rows=0,
                expected=0,
                actual=0,
                metric="null_count",
            )
        ]


class FakeBackend:
    pass


def test_executor_runs_dq_and_saves_result():

    store = InMemoryResultStore()

    executor = DQExecutor(
        engine=FakeEngine(),
        result_store=store,
    )

    result = executor.run(
        source=None,
        backend=FakeBackend(),
    )

    assert result is not None

    assert len(result.results) == 1

    assert (
            result.results[0].rule_name
            == "order_id_not_null"
    )

    assert len(store.results) == 1

    assert (
            store.results[0].run_id
            == result.run_id
    )


def test_executor_creates_valid_run_result():

    store = InMemoryResultStore()

    executor = DQExecutor(
        engine=FakeEngine(),
        result_store=store,
    )

    result = executor.run(
        source=None,
        backend=FakeBackend(),
    )

    assert result.run_id is not None

    assert result.started_at is not None

    assert result.finished_at is not None

    assert (
            result.finished_at
            >= result.started_at
    )

    assert result.success is True