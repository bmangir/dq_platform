class RuleRegistry:

    def __init__(self):
        self._rules = {}

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