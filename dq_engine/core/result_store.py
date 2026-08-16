from abc import ABC, abstractmethod
from uuid import UUID

from dq_engine.core.anomalies import AnomalyResult
from dq_engine.core.metrics import Metric
from dq_engine.core.results import RunResult


class ResultStore(ABC):

    @abstractmethod
    def save(
            self,
            run_result: RunResult,
    ) -> None:
        pass

    def save_metrics(
            self,
            metrics: list[Metric],
    ) -> None:
        raise NotImplementedError

    def save_anomalies(
            self,
            anomalies: list[AnomalyResult],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_run(
            self,
            run_id: UUID,
    ) -> RunResult | None:
        pass

    @abstractmethod
    def get_history(
            self,
            rule_name: str,
            limit: int = 30,
    ) -> list[RunResult]:
        pass

    @abstractmethod
    def get_metric_history(
            self,
            rule_name: str,
            metric_name: str,
            limit: int = 30,
    ) -> list[Metric]:
        pass

    def get_anomaly_history(
            self,
            rule_name: str,
            metric_name: str,
            limit: int = 30,
    ) -> list[AnomalyResult]:
        raise NotImplementedError