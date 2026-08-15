from dataclasses import dataclass
from uuid import UUID

from dq_engine.core.metrics import Metric


@dataclass
class AnomalyResult:
    run_id: UUID

    rule_name: str
    metric_name: str

    actual: float
    expected: float

    deviation: float
    score: float

    is_anomaly: bool

    method: str
    message: str