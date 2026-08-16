from datetime import datetime

from dq_engine.anomaly.engine import AnomalyEngine
from dq_engine.anomaly.factory import (
    AnomalyDetectorFactory,
)
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
            result_store,
            metric_extractor=None,
    ):
        self.config = config
        self.registry = registry
        self.result_store = result_store

        self.metric_extractor = (
                metric_extractor
                or MetricExtractor()
        )

    @classmethod
    def from_config(
            cls,
            path: str,
            registry,
            result_store,
            metric_extractor=None,
    ):
        loader = ConfigLoader()
        config = loader.load(path)

        return cls(
            config=config,
            registry=registry,
            result_store=result_store,
            metric_extractor=metric_extractor,
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

        metrics = self.metric_extractor.extract(
            run_result
        )

        # Detect anomalies using only historical metrics.
        # The current run must not be included in history.
        for check in self.config.checks:

            if not check.anomaly:
                continue

            if not check.anomaly.get(
                    "enabled",
                    False,
            ):
                continue

            matching_metrics = [
                metric
                for metric in metrics
                if metric.rule_name == check.name
            ]

            for metric in matching_metrics:

                history = (
                    self.result_store
                    .get_metric_history(
                        rule_name=metric.rule_name,
                        metric_name=metric.metric_name,
                        limit=check.anomaly.get(
                            "history_limit",
                            30,
                        ),
                    )
                )

                detector = (
                    AnomalyDetectorFactory.create(
                        check.anomaly
                    )
                )

                anomaly_engine = AnomalyEngine(
                    detector=detector
                )

                anomaly = anomaly_engine.detect(
                    metric=metric,
                    history=history,
                )

                run_result.anomalies.append(
                    anomaly
                )

        # Save the run FIRST because dq_metrics.run_id
        # has a foreign key to dq_runs.run_id.
        self.result_store.save(
            run_result
        )

        # Metrics are saved only after their parent run exists.
        if metrics:
            self.result_store.save_metrics(
                metrics
            )

        return run_result