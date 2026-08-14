from abc import ABC, abstractmethod

from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import (
    CheckResult,
    ExecutionPlan,
)


class BaseBackend(ABC):

    @abstractmethod
    def execute(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext,
    ) -> CheckResult:
        pass