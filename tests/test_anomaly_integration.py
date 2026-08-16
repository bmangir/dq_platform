from dq_engine.anomaly.engine import AnomalyEngine
from dq_engine.anomaly.factory import AnomalyDetectorFactory
from dq_engine.core.metric_extractor import MetricExtractor
from dq_engine.core.metrics import Metric
from dq_engine.core.results import RunResult
from dq_engine.core.run import RunContext
from dq_engine.storage.memory import InMemoryResultStore


def test_percentage_change_anomaly_end_to_end():

    store = InMemoryResultStore()

    detector = AnomalyDetectorFactory.create(
        {
            "method": "percentage_change",
            "threshold": 0.30,
            "min_history": 1,
        }
    )

    anomaly_engine = AnomalyEngine(
        detector=detector,
    )

    metric_extractor = MetricExtractor()

    # First run
    first_run = RunContext.create()

    first_result = RunResult(
        run_id=first_run.run_id,
        started_at=first_run.started_at,
        finished_at=first_run.started_at,
        results=[],
    )

    first_metric = Metric(
        run_id=first_run.run_id,
        rule_name="orders_row_count",
        rule_type="row_count",
        metric_name="row_count",
        value=5.0,
        timestamp=first_run.started_at,
    )

    store.save(first_result)
    store.save_metrics([first_metric])

    # Second run
    second_run = RunContext.create()

    second_result = RunResult(
        run_id=second_run.run_id,
        started_at=second_run.started_at,
        finished_at=second_run.started_at,
        results=[],
    )

    second_metric = Metric(
        run_id=second_run.run_id,
        rule_name="orders_row_count",
        rule_type="row_count",
        metric_name="row_count",
        value=10.0,
        timestamp=second_run.started_at,
    )

    history = store.get_metric_history(
        rule_name="orders_row_count",
        metric_name="row_count",
        limit=30,
    )

    anomaly = anomaly_engine.detect(
        metric=second_metric,
        history=history,
    )

    assert anomaly.is_anomaly is True

    assert anomaly.method == "percentage_change"

    assert anomaly.actual == 10.0

    assert anomaly.expected == 5.0

    assert anomaly.score == 1.0

    assert anomaly.deviation == 5.0

    store.save(second_result)
    store.save_metrics([second_metric])