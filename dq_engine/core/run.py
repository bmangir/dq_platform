from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from dq_engine.core.anomalies import AnomalyResult
from dq_engine.core.models import CheckResult


@dataclass
class RunContext:
    run_id: UUID
    started_at: datetime

    @classmethod
    def create(cls):
        return cls(
            run_id=uuid4(),
            started_at=datetime.utcnow(),
        )


@dataclass
class RunResult:
    run_id: UUID
    started_at: datetime
    finished_at: datetime
    results: list[CheckResult]

    @property
    def success(self) -> bool:
        if not self.results:
            return False

        return all(
            result.status.value == "PASSED"
            for result in self.results
        )