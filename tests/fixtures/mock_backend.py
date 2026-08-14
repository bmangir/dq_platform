from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
)
from dq_engine.backends.base import BaseBackend


class MockBackend(BaseBackend):

    def execute(self, plan, context):

        return CheckResult(
            rule_name=plan.rule_name,
            rule_type=plan.rule_type,
            status=CheckStatus.PASSED,
            severity=plan.severity,
            total_rows=100,
            failed_rows=0,
            expected=0,
            actual=0,
            message="Mock check passed.",
            execution_time_ms=1.0,
        )