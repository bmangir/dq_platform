from dq_engine.anomaly.base import AnomalyDetector
from dq_engine.core.anomalies import AnomalyResult
from dq_engine.core.metrics import Metric


class PercentageChangeDetector(AnomalyDetector):

    def __init__(
            self,
            threshold: float = 0.30,
            min_history: int = 1,
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
                method="percentage_change",
                message=(
                    "Insufficient historical data "
                    "for anomaly detection."
                ),
            )

        baseline = history[0].value

        if baseline == 0:

            is_anomaly = metric.value != 0

            score = (
                float("inf")
                if is_anomaly
                else 0.0
            )

        else:

            change = (
                             metric.value - baseline
                     ) / abs(baseline)

            score = abs(change)

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
            method="percentage_change",
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

        percentage = score * 100

        if is_anomaly:
            return (
                f"{metric.metric_name} changed by "
                f"{percentage:.2f}% compared with "
                f"the baseline."
            )

        return (
            f"{metric.metric_name} changed by "
            f"{percentage:.2f}%, within threshold."
        )