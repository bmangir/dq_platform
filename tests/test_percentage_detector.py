from datetime import datetime
from uuid import uuid4

from dq_engine.anomaly.percentage import (
    PercentageChangeDetector,
)
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


def test_percentage_detector_detects_large_change():

    history = [
        create_metric(10000),
    ]

    current = create_metric(15000)

    detector = PercentageChangeDetector(
        threshold=0.30,
    )

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is True
    assert result.score == 0.5
    assert result.actual == 15000
    assert result.expected == 10000


def test_percentage_detector_accepts_small_change():

    history = [
        create_metric(10000),
    ]

    current = create_metric(10500)

    detector = PercentageChangeDetector(
        threshold=0.30,
    )

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is False
    assert result.score == 0.05


def test_percentage_detector_detects_decrease():

    history = [
        create_metric(10000),
    ]

    current = create_metric(6000)

    detector = PercentageChangeDetector(
        threshold=0.30,
    )

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is True
    assert result.score == 0.4


def test_percentage_detector_handles_zero_baseline():

    history = [
        create_metric(0),
    ]

    current = create_metric(100)

    detector = PercentageChangeDetector(
        threshold=0.30,
    )

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is True
    assert result.score == float("inf")


def test_percentage_detector_accepts_zero_to_zero():

    history = [
        create_metric(0),
    ]

    current = create_metric(0)

    detector = PercentageChangeDetector(
        threshold=0.30,
    )

    result = detector.detect(
        metric=current,
        history=history,
    )

    assert result.is_anomaly is False
    assert result.score == 0.0