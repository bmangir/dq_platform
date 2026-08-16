from datetime import datetime, timedelta
from uuid import uuid4

from dq_engine.core.metrics import Metric
from dq_engine.storage.memory import (
    InMemoryResultStore,
)


def test_memory_store_returns_metric_history():

    store = InMemoryResultStore()

    run_id = uuid4()

    now = datetime.utcnow()

    metrics = [
        Metric(
            run_id=run_id,
            rule_name="orders_row_count",
            rule_type="row_count",
            metric_name="row_count",
            value=100.0,
            timestamp=now - timedelta(days=2),
        ),
        Metric(
            run_id=run_id,
            rule_name="orders_row_count",
            rule_type="row_count",
            metric_name="row_count",
            value=110.0,
            timestamp=now - timedelta(days=1),
        ),
        Metric(
            run_id=run_id,
            rule_name="orders_row_count",
            rule_type="row_count",
            metric_name="row_count",
            value=150.0,
            timestamp=now,
        ),
    ]

    store.save_metrics(metrics)

    history = store.get_metric_history(
        rule_name="orders_row_count",
        metric_name="row_count",
        limit=30,
    )

    assert len(history) == 3

    assert history[0].value == 150.0
    assert history[1].value == 110.0
    assert history[2].value == 100.0