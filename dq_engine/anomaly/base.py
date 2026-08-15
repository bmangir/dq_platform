from abc import ABC, abstractmethod

from dq_engine.core.anomalies import AnomalyResult
from dq_engine.core.metrics import Metric


class AnomalyDetector(ABC):

    @abstractmethod
    def detect(
            self,
            metric: Metric,
            history: list[Metric],
    ) -> AnomalyResult:
        pass