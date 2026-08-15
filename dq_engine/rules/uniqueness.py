from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import ExecutionPlan
from dq_engine.rules.base import BaseRule


class UniqueRule(BaseRule):

    rule_type = "unique"

    def build(
            self,
            context: ExecutionContext,
    ) -> ExecutionPlan:

        column = self.config.get("column")

        if not column:
            raise ValueError(
                f"Rule '{self.name}' requires a 'column'."
            )

        return ExecutionPlan(
            rule_name=self.name,
            rule_type=self.rule_type,
            severity=self.severity,
            operation="unique",
            parameters={
                "column": column,
            },
        )