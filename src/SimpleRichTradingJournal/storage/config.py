# Extract StorageConfig and StorageConfigManager from first artifact
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class StorageConfig:
    """Configuration for storage backends"""

    backend: str  # 'pickle', 'sqlite', 'mysql', 'postgresql'
    connection_string: str | None = None
    file_path: str | None = None
    table_prefix: str = "srtj_"

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "StorageConfig":
        return cls(**config)


# Storage configuration management
class StorageConfigManager:
    """Manages storage configuration for SRTJ"""

    DEFAULT_CONFIG = {
        "backend": "pickle",
        "file_path": None,  # Will be set to profile folder
        "table_prefix": "srtj_",
    }

    @classmethod
    def load_config(cls, profile_folder: str) -> dict[str, Any]:
        """Load storage configuration from profile folder"""
        config_file = Path(profile_folder) / "storage_config.json"

        if config_file.exists():
            import json

            with open(config_file) as f:
                config = json.load(f)
        else:
            config = cls.DEFAULT_CONFIG.copy()

        # Set default file_path to profile folder if not specified
        if not config.get("file_path"):
            config["file_path"] = profile_folder

        return config

    @classmethod
    def save_config(cls, profile_folder: str, config: dict[str, Any]) -> None:
        """Save storage configuration to profile folder"""
        config_file = Path(profile_folder) / "storage_config.json"

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
