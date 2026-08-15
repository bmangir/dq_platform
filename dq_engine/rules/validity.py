from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import ExecutionPlan
from dq_engine.rules.base import BaseRule


class AcceptedValuesRule(BaseRule):

    rule_type = "accepted_values"

    def build(
            self,
            context: ExecutionContext,
    ) -> ExecutionPlan:

        column = self.config.get("column")
        values = self.config.get("values")

        if not column:
            raise ValueError(
                f"Rule '{self.name}' requires a 'column'."
            )

        if not values:
            raise ValueError(
                f"Rule '{self.name}' requires "
                "at least one accepted value."
            )

        if not isinstance(values, list):
            raise ValueError(
                f"Rule '{self.name}' requires "
                "'values' to be a list."
            )

        return ExecutionPlan(
            rule_name=self.name,
            rule_type=self.rule_type,
            severity=self.severity,
            operation="accepted_values",
            parameters={
                "column": column,
                "values": values,
            },
        )


class RangeRule(BaseRule):

    rule_type = "range"

    def build(
            self,
            context: ExecutionContext,
    ) -> ExecutionPlan:

        column = self.config.get("column")
        minimum = self.config.get("min")
        maximum = self.config.get("max")

        if not column:
            raise ValueError(
                f"Rule '{self.name}' requires a 'column'."
            )

        if minimum is None and maximum is None:
            raise ValueError(
                f"Rule '{self.name}' requires "
                "at least one of 'min' or 'max'."
            )

        if (
                minimum is not None
                and maximum is not None
                and minimum > maximum
        ):
            raise ValueError(
                f"Rule '{self.name}' has an invalid range: "
                "'min' cannot be greater than 'max'."
            )

        return ExecutionPlan(
            rule_name=self.name,
            rule_type=self.rule_type,
            severity=self.severity,
            operation="range",
            parameters={
                "column": column,
                "min": minimum,
                "max": maximum,
            },
        )