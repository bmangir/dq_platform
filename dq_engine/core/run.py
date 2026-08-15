from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


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