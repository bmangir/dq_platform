from dq_engine.anomaly.factory import (
    AnomalyDetectorFactory,
)
from dq_engine.anomaly.percentage import (
    PercentageChangeDetector,
)
from dq_engine.anomaly.threshold import (
    ThresholdDetector,
)
from dq_engine.anomaly.zscore import (
    ZScoreDetector,
)


def test_factory_creates_zscore_detector():

    detector = AnomalyDetectorFactory.create(
        {
            "method": "z_score",
            "threshold": 3.0,
            "min_history": 5,
        }
    )

    assert isinstance(
        detector,
        ZScoreDetector,
    )

    assert detector.threshold == 3.0
    assert detector.min_history == 5


def test_factory_creates_percentage_detector():

    detector = AnomalyDetectorFactory.create(
        {
            "method": "percentage_change",
            "threshold": 0.25,
        }
    )

    assert isinstance(
        detector,
        PercentageChangeDetector,
    )

    assert detector.threshold == 0.25


def test_factory_creates_threshold_detector():

    detector = AnomalyDetectorFactory.create(
        {
            "method": "threshold",
            "threshold": 10,
            "direction": "above",
        }
    )

    assert isinstance(
        detector,
        ThresholdDetector,
    )

    assert detector.threshold == 10
    assert detector.direction == "above"


def test_factory_rejects_unknown_method():

    try:

        AnomalyDetectorFactory.create(
            {
                "method": "something_unknown",
            }
        )

        assert False

    except ValueError:
        assert True


def test_factory_supports_realistic_rule_config():

    anomaly_config = {
        "enabled": True,
        "method": "percentage_change",
        "threshold": 0.30,
        "min_history": 5,
    }

    detector = AnomalyDetectorFactory.create(
        anomaly_config
    )

    assert isinstance(
        detector,
        PercentageChangeDetector,
    )

    assert detector.threshold == 0.30
    assert detector.min_history == 5