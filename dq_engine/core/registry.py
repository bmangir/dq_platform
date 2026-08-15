from dq_engine.rules.completeness import (
    NotNullRule,
    RowCountRule,
)
from dq_engine.rules.uniqueness import UniqueRule
from dq_engine.rules.validity import (
    AcceptedValuesRule,
)


class RuleRegistry:

    def __init__(self):
        self._rules = {
            "not_null": NotNullRule,
            "row_count": RowCountRule,
            "unique": UniqueRule,
            "accepted_values": AcceptedValuesRule,
        }

    def register(self, rule_type, rule_class):
        self._rules[rule_type] = rule_class

    def get(self, rule_type):

        if rule_type not in self._rules:
            raise ValueError(
                f"Unknown rule type: {rule_type}"
            )

        return self._rules[rule_type]

    def create(self, rule_type, **kwargs):

        rule_class = self.get(rule_type)

        return rule_class(**kwargs)