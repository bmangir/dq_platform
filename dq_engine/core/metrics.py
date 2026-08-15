from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Metric:
    run_id: UUID

    rule_name: str
    rule_type: str

    metric_name: str
    value: float

    timestamp: datetime