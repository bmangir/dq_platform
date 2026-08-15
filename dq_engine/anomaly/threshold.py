from dq_engine.anomaly.base import AnomalyDetector
from dq_engine.core.anomalies import AnomalyResult
from dq_engine.core.metrics import Metric


class ThresholdDetector(AnomalyDetector):

    def __init__(
            self,
            threshold: float,
            direction: str = "above",
    ):
        if direction not in {
            "above",
            "below",
        }:
            raise ValueError(
                "direction must be 'above' or 'below'."
            )

        self.threshold = threshold
        self.direction = direction

    def detect(
            self,
            metric: Metric,
            history: list[Metric],
    ) -> AnomalyResult:

        if self.direction == "above":

            is_anomaly = (
                    metric.value > self.threshold
            )

        else:

            is_anomaly = (
                    metric.value < self.threshold
            )

        deviation = (
                metric.value - self.threshold
        )

        score = abs(deviation)

        return AnomalyResult(
            run_id=metric.run_id,
            rule_name=metric.rule_name,
            metric_name=metric.metric_name,
            actual=metric.value,
            expected=self.threshold,
            deviation=deviation,
            score=score,
            is_anomaly=is_anomaly,
            method="threshold",
            message=self._build_message(
                metric,
                is_anomaly,
            ),
        )

    def _build_message(
            self,
            metric: Metric,
            is_anomaly: bool,
    ) -> str:

        if is_anomaly:

            if self.direction == "above":
                return (
                    f"{metric.metric_name} value "
                    f"{metric.value} exceeded "
                    f"threshold {self.threshold}."
                )

            return (
                f"{metric.metric_name} value "
                f"{metric.value} fell below "
                f"threshold {self.threshold}."
            )

        return (
            f"{metric.metric_name} value "
            f"{metric.value} is within "
            f"threshold {self.threshold}."
        )