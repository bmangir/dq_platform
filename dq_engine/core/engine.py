from datetime import datetime

from dq_engine.anomaly.engine import AnomalyEngine
from dq_engine.config.loader import ConfigLoader
from dq_engine.core.context import ExecutionContext
from dq_engine.core.metric_extractor import MetricExtractor
from dq_engine.core.results import RunResult
from dq_engine.core.run import RunContext


class DQEngine:

    def __init__(
            self,
            config,
            registry,
            result_store=None,
            anomaly_engine: AnomalyEngine | None = None,
    ):
        self.config = config
        self.registry = registry
        self.result_store = result_store
        self.anomaly_engine = anomaly_engine
        self.metric_extractor = MetricExtractor()

    @classmethod
    def from_config(
            cls,
            path: str,
            registry,
            result_store=None,
            anomaly_engine: AnomalyEngine | None = None,
    ):
        loader = ConfigLoader()
        config = loader.load(path)

        return cls(
            config=config,
            registry=registry,
            result_store=result_store,
            anomaly_engine=anomaly_engine,
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

        run_result = RunResult(
            run_id=run_context.run_id,
            started_at=run_context.started_at,
            finished_at=datetime.utcnow(),
            results=results,
        )

        return run_result