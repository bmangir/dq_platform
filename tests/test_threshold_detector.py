from datetime import datetime
from uuid import uuid4

from dq_engine.anomaly.threshold import (
    ThresholdDetector,
)
from dq_engine.core.metrics import Metric


def create_metric(value: float) -> Metric:

    return Metric(
        run_id=uuid4(),
        rule_name="order_id_not_null",
        rule_type="not_null",
        metric_name="null_count",
        value=value,
        timestamp=datetime.utcnow(),
    )


def test_threshold_detector_detects_value_above_threshold():

    current = create_metric(10)

    detector = ThresholdDetector(
        threshold=0,
        direction="above",
    )

    result = detector.detect(
        metric=current,
        history=[],
    )

    assert result.is_anomaly is True
    assert result.actual == 10
    assert result.expected == 0
    assert result.method == "threshold"


def test_threshold_detector_accepts_value_within_threshold():

    current = create_metric(0)

    detector = ThresholdDetector(
        threshold=0,
        direction="above",
    )

    result = detector.detect(
        metric=current,
        history=[],
    )

    assert result.is_anomaly is False


def test_threshold_detector_detects_value_below_threshold():

    current = create_metric(5)

    detector = ThresholdDetector(
        threshold=10,
        direction="below",
    )

    result = detector.detect(
        metric=current,
        history=[],
    )

    assert result.is_anomaly is True


def test_threshold_detector_rejects_invalid_direction():

    try:
        ThresholdDetector(
            threshold=10,
            direction="invalid",
        )

        assert False

    except ValueError:
        assert True