from datetime import datetime

from dq_engine.core.executor import DQExecutor
from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
    Severity,
)
from dq_engine.core.metric_extractor import (
    MetricExtractor,
)
from dq_engine.core.run import RunContext


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


class FakeResultStore:

    def __init__(self):
        self.saved = []

    def save(self, run_result):
        self.saved.append(run_result)


def test_executor_runs_and_persists_result():

    store = FakeResultStore()

    executor = DQExecutor(
        engine=FakeEngine(),
        result_store=store,
        metric_extractor=MetricExtractor(),
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

    assert len(store.saved) == 1

    assert (
            store.saved[0].run_id
            == result.run_id
    )