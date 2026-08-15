from datetime import datetime

from dq_engine.core.metric_extractor import (
    MetricExtractor,
)
from dq_engine.core.run import (
    RunContext,
    RunResult,
)


class DQExecutor:

    def __init__(
            self,
            engine,
            result_store,
            metric_extractor,
            anomaly_engine=None,
    ):
        self.engine = engine
        self.result_store = result_store
        self.metric_extractor = metric_extractor
        self.anomaly_engine = anomaly_engine

    def run(
            self,
            source,
            backend,
    ):

        context = RunContext.create()

        results = self.engine.run(
            source=source,
            backend=backend,
        )

        finished_at = datetime.utcnow()

        run_result = RunResult(
            run_id=context.run_id,
            started_at=context.started_at,
            finished_at=finished_at,
            results=results,
        )

        self.result_store.save(
            run_result
        )

        return run_result