from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import ExecutionPlan
from dq_engine.rules.base import BaseRule


class NotNullRule(BaseRule):

    rule_type = "not_null"

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
            operation="count_nulls",
            parameters={
                "column": column,
            },
        )


class RowCountRule(BaseRule):

    rule_type = "row_count"

    def build(
            self,
            context: ExecutionContext,
    ) -> ExecutionPlan:

        threshold = self.config.get(
            "threshold",
            {},
        )

        min_rows = threshold.get("min")
        max_rows = threshold.get("max")

        if min_rows is None and max_rows is None:
            raise ValueError(
                f"Rule '{self.name}' requires "
                "at least one row count threshold."
            )

        if (
                min_rows is not None
                and max_rows is not None
                and min_rows > max_rows
        ):
            raise ValueError(
                f"Rule '{self.name}' has invalid "
                "row count thresholds: min > max."
            )

        return ExecutionPlan(
            rule_name=self.name,
            rule_type=self.rule_type,
            severity=self.severity,
            operation="row_count",
            parameters={
                "min": min_rows,
                "max": max_rows,
            },
        )