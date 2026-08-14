import yaml

from dq_engine.config.schema import (
    ConfigValidator,
    DQConfig,
)


class ConfigLoader:

    def __init__(self):
        self.validator = ConfigValidator()

    def load(self, path: str) -> DQConfig:

        with open(path, "r") as file:
            raw_config = yaml.safe_load(file)

        return self.validator.validate(raw_config)