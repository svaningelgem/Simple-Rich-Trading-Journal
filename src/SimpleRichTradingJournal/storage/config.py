# Extract StorageConfig and StorageConfigManager from first artifact
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class StorageConfig:
    """Configuration for storage backends"""

    backend: str  # 'pickle', 'sqlite', 'mysql', 'postgresql'
    connection_string: Optional[str] = None
    file_path: Optional[str] = None
    table_prefix: str = "srtj_"

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "StorageConfig":
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
    def load_config(cls, profile_folder: str) -> Dict[str, Any]:
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
    def save_config(cls, profile_folder: str, config: Dict[str, Any]) -> None:
        """Save storage configuration to profile folder"""
        config_file = Path(profile_folder) / "storage_config.json"

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
