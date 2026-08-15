from datetime import datetime
from uuid import uuid4

from dq_engine.core.metrics import Metric
from dq_engine.storage.memory import (
    InMemoryResultStore,
)


def test_memory_result_store_saves_metrics():

    store = InMemoryResultStore()

    run_id = uuid4()

    metric = Metric(
        run_id=run_id,
        rule_name="orders_row_count",
        rule_type="row_count",
        metric_name="row_count",
        value=5.0,
        timestamp=datetime.utcnow(),
    )

    store.save_metrics([metric])

    assert len(store.metrics) == 1

    saved_metric = store.metrics[0]

    assert saved_metric.run_id == run_id
    assert saved_metric.rule_name == "orders_row_count"
    assert saved_metric.metric_name == "row_count"
    assert saved_metric.value == 5.0