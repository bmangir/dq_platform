import yaml


class ConfigLoader:

    def load(self, path: str) -> dict:
        with open(path, "r") as file:
            return yaml.safe_load(file)