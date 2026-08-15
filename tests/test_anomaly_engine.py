from datetime import datetime
from uuid import uuid4

from dq_engine.anomaly.engine import AnomalyEngine
from dq_engine.anomaly.zscore import ZScoreDetector
from dq_engine.core.metrics import Metric


def create_metric(value: float) -> Metric:

    return Metric(
        run_id=uuid4(),
        rule_name="orders_row_count",
        rule_type="row_count",
        metric_name="row_count",
        value=value,
        timestamp=datetime.utcnow(),
    )


def test_anomaly_engine_uses_detector():

    history = [
        create_metric(10000),
        create_metric(10100),
        create_metric(9900),
        create_metric(10050),
        create_metric(9950),
    ]

    current = create_metric(18000)

    detector = ZScoreDetector(
        threshold=3.0,
        min_history=5,
    )

    engine = AnomalyEngine(
        detector=detector,
    )

    result = engine.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is True
    assert result.method == "z_score"