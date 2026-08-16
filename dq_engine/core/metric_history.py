from abc import ABC, abstractmethod

from dq_engine.core.metrics import Metric


class MetricHistoryProvider(ABC):

    @abstractmethod
    def get_metric_history(
            self,
            rule_name: str,
            metric_name: str,
            limit: int = 30,
    ) -> list[Metric]:
        pass