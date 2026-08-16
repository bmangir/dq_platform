from uuid import UUID

from dq_engine.core.anomalies import AnomalyResult
from dq_engine.core.metrics import Metric
from dq_engine.core.result_store import ResultStore
from dq_engine.core.results import RunResult


class InMemoryResultStore(ResultStore):

    def __init__(self):
        self._results: list[RunResult] = []
        self._metrics: list[Metric] = []
        self._anomalies: list[AnomalyResult] = []

    def save(
            self,
            run_result: RunResult,
    ) -> None:
        self._results.append(run_result)

    def save_metrics(
            self,
            metrics: list[Metric],
    ) -> None:
        self._metrics.extend(metrics)

    def save_anomalies(
            self,
            anomalies: list[AnomalyResult],
    ) -> None:
        self._anomalies.extend(anomalies)

    @property
    def results(self) -> list[RunResult]:
        return self._results

    @property
    def metrics(self) -> list[Metric]:
        return self._metrics

    @property
    def anomalies(self) -> list[AnomalyResult]:
        return self._anomalies

    def get_run(
            self,
            run_id: UUID,
    ) -> RunResult | None:

        for result in self._results:

            if result.run_id == run_id:
                return result

        return None

    def get_history(
            self,
            rule_name: str,
            limit: int = 30,
    ) -> list[RunResult]:

        matched = []

        for run_result in reversed(self._results):

            if any(
                    result.rule_name == rule_name
                    for result in run_result.results
            ):
                matched.append(run_result)

            if len(matched) >= limit:
                break

        return matched

    def get_metric_history(
            self,
            rule_name: str,
            metric_name: str,
            limit: int = 30,
    ) -> list[Metric]:

        matched = [
            metric
            for metric in reversed(self._metrics)
            if (
                    metric.rule_name == rule_name
                    and metric.metric_name == metric_name
            )
        ]

        return matched[:limit]

    def get_anomaly_history(
            self,
            rule_name: str,
            metric_name: str,
            limit: int = 30,
    ) -> list[AnomalyResult]:

        matched = [
            anomaly
            for anomaly in reversed(self._anomalies)
            if (
                    anomaly.rule_name == rule_name
                    and anomaly.metric_name == metric_name
            )
        ]

        return matched[:limit]