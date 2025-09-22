"""Configuration loader with YAML support and validation."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

import yaml
from pydantic import ValidationError

from .models import Config

T = TypeVar('T')

# Global config instance
_config_instance: Optional[Config] = None


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
    def load_from_file(config_path: Optional[Path] = None, profile_folder: Optional[str] = None) -> Config:
        """Load and validate configuration from file."""
        if config_path is None:
            config_path = ConfigLoader._find_config_file(profile_folder)

        print(f"Loading config from: {config_path}")

        # Load the YAML data
        config_data = ConfigLoader.load_yaml(config_path)

        # Validate and create config instance
        try:
            return Config.model_validate(config_data)
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
        default_config = Config(themes=None)  # Themes will be set to None initially

        # Convert to dict and clean up for YAML output
        config_dict = default_config.model_dump(exclude={'themes'})

        # Add theme include directive
        config_dict['themes'] = '!include ui/themes/dark.yaml'

        # Write to file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False, indent=2)

        print(f"Example configuration created at: {output_path}")


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        raise RuntimeError(
            "Configuration not initialized. Call init_config() first."
        )
    return _config_instance


def init_config(profile_folder: Optional[str] = None, config_path: Optional[Path] = None) -> Config:
    """Initialize the global configuration instance."""
    global _config_instance
    _config_instance = ConfigLoader.load_from_file(config_path, profile_folder)
    return _config_instance


def reload_config(profile_folder: Optional[str] = None, config_path: Optional[Path] = None) -> Config:
    """Reload the configuration from disk."""
    global _config_instance
    _config_instance = ConfigLoader.load_from_file(config_path, profile_folder)
    return _config_instance


# Convenience functions for accessing config sections
def app() -> 'AppConfig':
    """Get app configuration."""
    return get_config().app


def ui() -> 'UIConfig':
    """Get UI configuration."""
    return get_config().ui


def themes() -> 'ThemeConfig':
    """Get theme configuration."""
    return get_config().themes


def storage() -> 'StorageConfig':
    """Get storage configuration."""
    return get_config().storage


def log() -> 'LogConfig':
    """Get log configuration."""
    return get_config().log


def statistics() -> 'StatisticsConfig':
    """Get statistics configuration."""
    return get_config().statistics


def balance() -> 'BalanceConfig':
    """Get balance configuration."""
    return get_config().balance


def notes() -> 'NotesConfig':
    """Get notes configuration."""
    return get_config().notes


def plugins() -> 'PluginsConfig':
    """Get plugins configuration."""
    return get_config().plugins


def scope() -> 'ScopeConfig':
    """Get scope configuration."""
    return get_config().scope


def maintenance() -> 'MaintenanceConfig':
    """Get maintenance configuration."""
    return get_config().maintenance


def startup() -> 'StartupConfig':
    """Get startup configuration."""
    return get_config().startup