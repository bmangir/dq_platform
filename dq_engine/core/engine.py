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

    def run(
            self,
            source,
            backend,
    ):

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

        finished_at = datetime.utcnow()

        run_result = RunResult(
            run_id=run_context.run_id,
            started_at=run_context.started_at,
            finished_at=finished_at,
            results=results,
        )

        metrics = MetricExtractor().extract(
            run_result
        )

        anomalies = []

        if self.anomaly_engine is not None:

            for metric in metrics:

                check = next(
                    (
                        check
                        for check in self.config.checks
                        if check.name == metric.rule_name
                    ),
                    None,
                )

                if check is None:
                    continue

                anomaly_config = check.anomaly

                if not anomaly_config:
                    continue

                if not anomaly_config.get(
                        "enabled",
                        False,
                ):
                    continue

                history = []

                if self.result_store is not None:

                    history = (
                        self.result_store.get_metric_history(
                            rule_name=metric.rule_name,
                            metric_name=metric.metric_name,
                            limit=anomaly_config.get(
                                "min_history",
                                30,
                            ),
                        )
                    )

                anomaly_result = (
                    self.anomaly_engine.detect(
                        metric=metric,
                        history=history,
                    )
                )

                anomalies.append(
                    anomaly_result
                )

        run_result.anomalies = anomalies

        if self.result_store is not None:

            self.result_store.save(
                run_result
            )

            if metrics:
                self.result_store.save_metrics(
                    metrics
                )

        return run_result