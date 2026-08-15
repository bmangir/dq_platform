from dq_engine.core.metrics import Metric
from dq_engine.core.results import RunResult


class MetricExtractor:

    def extract(
            self,
            run_result: RunResult,
    ) -> list[Metric]:

        metrics = []

        for result in run_result.results:

            if result.metric is None:
                continue

            if result.actual is None:
                continue

            if not isinstance(
                    result.actual,
                    (int, float),
            ):
                continue

            metrics.append(
                Metric(
                    run_id=run_result.run_id,
                    rule_name=result.rule_name,
                    rule_type=result.rule_type,
                    metric_name=result.metric,
                    value=float(result.actual),
                    timestamp=run_result.finished_at,
                )
            )

        return metrics