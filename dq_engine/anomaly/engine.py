from dq_engine.anomaly.base import AnomalyDetector
from dq_engine.core.anomalies import AnomalyResult
from dq_engine.core.metrics import Metric


class AnomalyEngine:

    def __init__(
            self,
            detector: AnomalyDetector,
    ):
        self.detector = detector

    def detect(
            self,
            metric: Metric,
            history: list[Metric],
    ) -> AnomalyResult:

        return self.detector.detect(
            metric=metric,
            history=history,
        )