from dq_engine.anomaly.engine import AnomalyEngine
from dq_engine.anomaly.factory import AnomalyDetectorFactory
from dq_engine.backends.postgres import PostgresBackend
from dq_engine.core.engine import DQEngine
from dq_engine.core.metrics import Metric
from dq_engine.core.registry import RuleRegistry
from dq_engine.database.connection import (
    get_postgres_connection_string,
)
from dq_engine.storage.postgres import PostgresResultStore


def test_engine_runs_anomaly_detection_with_postgres_history(
        valid_orders_data,
):

    registry = RuleRegistry()

    store = PostgresResultStore(
        get_postgres_connection_string()
    )

    anomaly_engine = AnomalyEngine(
        detector=AnomalyDetectorFactory.create(
            {
                "method": "threshold",
                "threshold": 0,
                "direction": "above",
            }
        )
    )

    engine = DQEngine.from_config(
        "configs/examples/orders_anomaly.yaml",
        registry=registry,
        result_store=store,
        anomaly_engine=anomaly_engine,
    )

    backend = PostgresBackend(
        connection_string=(
            get_postgres_connection_string()
        )
    )

    run_result = engine.run(
        source=None,
        backend=backend,
    )

    assert run_result.run_id is not None
    assert run_result.finished_at is not None