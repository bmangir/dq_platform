from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from dq_engine.core.models import CheckResult, CheckStatus


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
            result.status == CheckStatus.PASSED
            for result in self.results
        )