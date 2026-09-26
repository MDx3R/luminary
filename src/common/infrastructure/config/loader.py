import os
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, cast

import yaml
from dotenv import load_dotenv
from pydantic.fields import FieldInfo
from pydantic_settings import PydanticBaseSettingsSource


class ConfigLoader:
    def __init__(self, config_dir: str = "configs") -> None:
        self.config_dir = Path(config_dir)

    def load(self, config: str | None = None) -> dict[str, Any]:
        data = self.load_yaml(self.config_dir / "base.yaml")

        if config:
            path = self.config_dir / config
            config_data = self.load_yaml(path)
        else:
            path = self.fetch_config_path()
            config_data = self.load_yaml(path)

        self.update(data, config_data)
        self.override(data, os.environ.copy())
        return data

    def update(self, data: dict[str, Any], overrides: dict[str, Any]) -> None:
        self.merge(data, overrides)

    def override(self, data: dict[str, Any], overrides: dict[str, Any]) -> None:
        # NOTE: overrides values should be plain
        # NOTE: all fields with same name will be overriden
        for key, value in data.items():
            if isinstance(value, dict):
                self.override(cast(dict[str, Any], value), overrides)
                continue
            for k, v in overrides.items():
                if k.lower() == key.lower():
                    data[key] = v

    def merge(self, data: dict[str, Any], overrides: dict[str, Any]) -> None:
        # NOTE: overrides values should follow data structure
        for k, v in overrides.items():
            if isinstance(v, dict):
                node = data.setdefault(k, {})
                self.merge(node, cast(dict[str, Any], v))
            else:
                data[k] = v

    def load_yaml(self, path: str | Path) -> dict[str, Any]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found at: {path}")
        with path.open("r") as f:
            return yaml.safe_load(f) or {}

    def fetch_config_path(self) -> Path:
        """Fetch the configuration file path.

        1. --config
        2. ENV CONFIG_PATH
        3. default configs/config.yaml
        """
        default = "configs/config.yaml"

        parser = ArgumentParser(description="Load config path")
        parser.add_argument("--config", type=str, help="Path to config file")
        args, _ = parser.parse_known_args()

        load_dotenv(override=False)
        return Path(args.config or os.getenv("CONFIG_PATH") or default)


class MergeSettingsSource(PydanticBaseSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        # Nothing to do here. Only implement the return statement to make mypy happy
        return None, "", False

    def __call__(self) -> dict[str, Any]:
        return ConfigLoader().load()
