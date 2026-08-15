from statistics import mean, stdev

from dq_engine.core.anomalies import AnomalyResult
from dq_engine.core.metrics import Metric


class ZScoreDetector:

    def __init__(
            self,
            threshold: float = 3.0,
            min_history: int = 5,
    ):
        self.threshold = threshold
        self.min_history = min_history

    def detect(
            self,
            metric: Metric,
            history: list[Metric],
    ) -> AnomalyResult:

        if len(history) < self.min_history:
            return AnomalyResult(
                run_id=metric.run_id,
                rule_name=metric.rule_name,
                metric_name=metric.metric_name,
                actual=metric.value,
                expected=0.0,
                deviation=0.0,
                score=0.0,
                is_anomaly=False,
                method="z_score",
                message=(
                    "Insufficient historical data "
                    "for anomaly detection."
                ),
            )

        values = [
            item.value
            for item in history
        ]

        baseline = mean(values)

        standard_deviation = stdev(values)

        if standard_deviation == 0:
            is_anomaly = (
                    metric.value != baseline
            )

            score = (
                float("inf")
                if is_anomaly
                else 0.0
            )

        else:
            score = abs(
                metric.value - baseline
            ) / standard_deviation

            is_anomaly = (
                    score >= self.threshold
            )

        deviation = (
                metric.value - baseline
        )

        return AnomalyResult(
            run_id=metric.run_id,
            rule_name=metric.rule_name,
            metric_name=metric.metric_name,
            actual=metric.value,
            expected=baseline,
            deviation=deviation,
            score=score,
            is_anomaly=is_anomaly,
            method="z_score",
            message=self._build_message(
                metric,
                baseline,
                score,
                is_anomaly,
            ),
        )

    @staticmethod
    def _build_message(
            metric: Metric,
            baseline: float,
            score: float,
            is_anomaly: bool,
    ) -> str:

        if is_anomaly:
            return (
                f"{metric.metric_name} value "
                f"{metric.value} is anomalous. "
                f"Expected approximately "
                f"{baseline:.2f}, "
                f"z-score={score:.2f}."
            )

        return (
            f"{metric.metric_name} value "
            f"{metric.value} is within "
            f"expected range."
        )