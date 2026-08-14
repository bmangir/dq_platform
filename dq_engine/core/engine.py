from dq_engine.config.loader import ConfigLoader


class DQEngine:

    def __init__(self, config: dict, registry):
        self.config = config
        self.registry = registry

    @classmethod
    def from_config(cls, path: str, registry):
        loader = ConfigLoader()
        config = loader.load(path)

        return cls(
            config=config,
            registry=registry
        )

    def run(self, source, backend):
        pass