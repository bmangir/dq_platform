from datetime import datetime

from dq_engine.core.results import RunResult
from dq_engine.core.run import RunContext
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

        run_context = RunContext.create()

        context = ExecutionContext(
            source=source,
            table=self.config.table.name,
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

        return RunResult(
            run_id=run_context.run_id,
            started_at=run_context.started_at,
            finished_at=datetime.utcnow(),
            results=results,
        )