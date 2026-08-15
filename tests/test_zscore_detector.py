from dq_engine.anomaly.zscore import ZScoreDetector
from dq_engine.core.metrics import Metric
from uuid import uuid4
from datetime import datetime


def create_metric(value: float) -> Metric:

    return Metric(
        run_id=uuid4(),
        rule_name="orders_row_count",
        rule_type="row_count",
        metric_name="row_count",
        value=value,
        timestamp=datetime.utcnow(),
    )


def test_zscore_detector_detects_normal_value():

    history = [
        create_metric(10000),
        create_metric(10100),
        create_metric(9900),
        create_metric(10050),
        create_metric(9950),
    ]

    current = create_metric(10020)

    detector = ZScoreDetector(
        threshold=3.0,
        min_history=5,
    )

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is False
    assert result.method == "z_score"
    assert result.actual == 10020


def test_zscore_detector_detects_anomaly():

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

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is True
    assert result.score >= 3.0
    assert result.actual == 18000
    assert result.expected < 11000


def test_zscore_detector_requires_minimum_history():

    history = [
        create_metric(10000),
        create_metric(10100),
    ]

    current = create_metric(18000)

    detector = ZScoreDetector(
        threshold=3.0,
        min_history=5,
    )

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is False
    assert result.score == 0.0
    assert (
            "Insufficient historical data"
            in result.message
    )


def test_zscore_detector_handles_zero_standard_deviation():

    history = [
        create_metric(100),
        create_metric(100),
        create_metric(100),
        create_metric(100),
        create_metric(100),
    ]

    current = create_metric(200)

    detector = ZScoreDetector(
        threshold=3.0,
        min_history=5,
    )

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is True
    assert result.score == float("inf")


def test_zscore_detector_handles_constant_normal_value():

    history = [
        create_metric(100),
        create_metric(100),
        create_metric(100),
        create_metric(100),
        create_metric(100),
    ]

    current = create_metric(100)

    detector = ZScoreDetector(
        threshold=3.0,
        min_history=5,
    )

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is False
    assert result.score == 0.0