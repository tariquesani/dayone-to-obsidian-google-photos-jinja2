import yaml


class Config:
    _config = None

    @classmethod
    def load_config(cls, config_file):
        with open(config_file, "r") as file:
            cls._config = yaml.safe_load(file)

    @classmethod
    def get(cls, key, default=None):
        return cls._config.get(key, default)
