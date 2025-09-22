"""Configuration loader with YAML support and validation."""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar

import yaml
from pydantic import ValidationError

from .models import (
    Config as ConfigModel,
    AppConfig,
    UIConfig,
    ThemeConfig,
    StorageConfig,
    LogConfig,
    StatisticsConfig,
    BalanceConfig,
    NotesConfig,
    PluginsConfig,
    ScopeConfig,
    MaintenanceConfig,
    StartupConfig,
)


class IncludeLoader(yaml.SafeLoader):
    """YAML loader with !include support for modular config files."""

    def __init__(self, stream):
        self._root = Path(stream.name).parent if hasattr(stream, 'name') else Path.cwd()
        super().__init__(stream)


def include_constructor(loader: IncludeLoader, node: yaml.Node) -> Any:
    """Include constructor for YAML files."""
    filename = loader.construct_scalar(node)
    filepath = loader._root / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Included file not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.load(f, IncludeLoader)


# Register the include constructor
IncludeLoader.add_constructor('!include', include_constructor)


class ConfigLoader:
    """Handles loading and validation of SRTJ configuration."""

    @staticmethod
    def _find_config_file(profile_folder: Optional[str] = None) -> Path:
        """Find the config.yaml file in order of preference."""
        search_paths = []

        if profile_folder:
            search_paths.append(Path(profile_folder) / "config.yaml")

        # Check current working directory
        search_paths.append(Path.cwd() / "config.yaml")

        # Check alongside the script
        if hasattr(sys, '_MEIPASS'):
            # Running as PyInstaller bundle
            search_paths.append(Path(sys._MEIPASS) / "config.yaml")
        else:
            # Running as script
            script_dir = Path(__file__).parent.parent
            search_paths.append(script_dir / "config.yaml")

        # Check system config locations
        if os.name == 'posix':
            search_paths.extend([
                Path.home() / ".config" / "srtj" / "config.yaml",
                Path("/etc/srtj/config.yaml")
            ])
        elif os.name == 'nt':
            if appdata := os.environ.get('APPDATA'):
                search_paths.append(Path(appdata) / "SRTJ" / "config.yaml")

        for path in search_paths:
            if path.exists():
                return path

        raise FileNotFoundError(
            f"config.yaml not found in any of: {[str(p) for p in search_paths]}"
        )

    @staticmethod
    def load_yaml(config_path: Path) -> Dict[str, Any]:
        """Load YAML configuration with include support."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.load(f, IncludeLoader)
            return data or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {config_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {config_path}: {e}")

    @staticmethod
    def load_from_file(config_path: Optional[Path] = None, profile_folder: Optional[str] = None) -> 'Config':
        """Load and validate configuration from file."""
        if config_path is None:
            config_path = ConfigLoader._find_config_file(profile_folder)

        print(f"Loading config from: {config_path}")

        # Load the YAML data
        config_data = ConfigLoader.load_yaml(config_path)

        # Validate and create config instance
        try:
            config_model = ConfigModel.model_validate(config_data)
            return Config(config_model)
        except ValidationError as e:
            print(f"Configuration validation failed:")
            for error in e.errors():
                loc = " -> ".join(str(x) for x in error['loc'])
                print(f"  {loc}: {error['msg']}")
            raise SystemExit("Configuration validation failed. Please check your config.yaml file.")

    @staticmethod
    def create_example_config(output_path: Path) -> None:
        """Create an example configuration file."""
        # Create a default config instance
        default_config = ConfigModel(themes=None)  # Themes will be set to None initially

        # Convert to dict and clean up for YAML output
        config_dict = default_config.model_dump(exclude={'themes'})

        # Add theme include directive
        config_dict['themes'] = '!include ui/themes/dark.yaml'

        # Write to file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False, indent=2)

        print(f"Example configuration created at: {output_path}")


@dataclass
class Config:
    """Configuration wrapper with property-based access."""

    _config: ConfigModel

    @property
    def app(self) -> AppConfig:
        """Get app configuration."""
        return self._config.app

    @property
    def startup(self) -> StartupConfig:
        """Get startup configuration."""
        return self._config.startup

    @property
    def ui(self) -> UIConfig:
        """Get UI configuration."""
        return self._config.ui

    @property
    def scope(self) -> ScopeConfig:
        """Get scope configuration."""
        return self._config.scope

    @property
    def log(self) -> LogConfig:
        """Get log configuration."""
        return self._config.log

    @property
    def balance(self) -> BalanceConfig:
        """Get balance configuration."""
        return self._config.balance

    @property
    def statistics(self) -> StatisticsConfig:
        """Get statistics configuration."""
        return self._config.statistics

    @property
    def notes(self) -> NotesConfig:
        """Get notes configuration."""
        return self._config.notes

    @property
    def plugins(self) -> PluginsConfig:
        """Get plugins configuration."""
        return self._config.plugins

    @property
    def storage(self) -> StorageConfig:
        """Get storage configuration."""
        return self._config.storage

    @property
    def maintenance(self) -> MaintenanceConfig:
        """Get maintenance configuration."""
        return self._config.maintenance

    @property
    def themes(self) -> ThemeConfig:
        """Get theme configuration."""
        return self._config.themes

    def init(self, profile_folder: Optional[str] = None, config_path: Optional[Path] = None) -> None:
        ConfigLoader.load_from_file(config_path, profile_folder)

    reload = init


config: Config | None = None
