from dq_engine.anomaly.base import AnomalyDetector
from dq_engine.anomaly.percentage import (
    PercentageChangeDetector,
)
from dq_engine.anomaly.threshold import (
    ThresholdDetector,
)
from dq_engine.anomaly.zscore import (
    ZScoreDetector,
)


class AnomalyDetectorFactory:

    @staticmethod
    def create(
            config: dict,
    ) -> AnomalyDetector:

        method = config.get("method")

        if method == "z_score":

            return ZScoreDetector(
                threshold=config.get(
                    "threshold",
                    3.0,
                ),
                min_history=config.get(
                    "min_history",
                    5,
                ),
            )

        if method == "percentage_change":

            return PercentageChangeDetector(
                threshold=config.get(
                    "threshold",
                    0.30,
                ),
                min_history=config.get(
                    "min_history",
                    1,
                ),
            )

        if method == "threshold":

            return ThresholdDetector(
                threshold=config["threshold"],
                direction=config.get(
                    "direction",
                    "above",
                ),
            )

        raise ValueError(
            f"Unsupported anomaly method: {method}"
        )