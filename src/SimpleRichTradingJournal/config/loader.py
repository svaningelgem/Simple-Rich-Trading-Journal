"""Configuration loader with YAML support and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, ClassVar

import yaml
from logprise import logger
from pydantic import ValidationError

from .models import Config as ConfigModel


class IncludeLoader(yaml.SafeLoader):
    """YAML loader with !include support for modular config files."""

    def __init__(self, stream) -> None:
        self._root = Path(stream.name).parent if hasattr(stream, "name") else Path.cwd()
        super().__init__(stream)


def include_constructor(loader: IncludeLoader, node: yaml.Node) -> Any:
    """Include constructor for YAML files."""
    filename = loader.construct_scalar(node)
    filepath = loader._root / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Included file not found: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        return yaml.load(f, IncludeLoader)


# Register the include constructor
IncludeLoader.add_constructor("!include", include_constructor)


class ConfigManager:
    """Singleton configuration manager."""

    _instance: ClassVar[ConfigManager | None] = None
    _config: ConfigModel

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize configuration on first access."""
        profile_folder = os.environ.get("SRTJ_PROFILE")
        config_path = self._find_config_file(profile_folder)
        self._load(config_path)

    def _find_config_file(self, profile_folder: str | None = None) -> Path:
        """Find the config.yaml file."""
        # (keep existing logic from ConfigLoader._find_config_file)

    def _load(self, config_path: Path):
        """Load and validate configuration."""
        try:
            with open(config_path, encoding="utf-8") as f:
                data = yaml.load(f, IncludeLoader)
            self._config = ConfigModel.model_validate(data or {})
        except (yaml.YAMLError, ValidationError) as e:
            logger.error(f"Configuration error: {e}")
            raise SystemExit("Configuration validation failed")

    def reload(self, profile_folder: str | None = None):
        """Reload configuration."""
        config_path = self._find_config_file(profile_folder)
        self._load(config_path)

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to config model."""
        return getattr(self._config, name)


# Global singleton instance
config = ConfigManager()
