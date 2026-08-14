from dq_engine.config.loader import ConfigLoader
from dq_engine.core.context import ExecutionContext


class DQEngine:

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry

    @classmethod
    def from_config(cls, path: str, registry):
        loader = ConfigLoader()
        config = loader.load(path)

        return cls(
            config=config,
            registry=registry,
        )

    def run(self, source, backend):

        context = ExecutionContext(
            source=source,
            table=self.config.table,
        )

        results = []

        for check in self.config.checks:

            rule = self.registry.create(
                rule_type=check.type,
                name=check.name,
                severity=check.severity,
                **check.parameters,
            )

            plan = rule.build(context)

            result = backend.execute(
                plan=plan,
                context=context,
            )

            results.append(result)

        return results