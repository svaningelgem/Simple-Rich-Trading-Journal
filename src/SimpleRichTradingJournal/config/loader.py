from pathlib import Path
from typing import Optional
import yaml
from .models import Config

def load_config(path: Optional[Path] = None) -> Config:
    """Load and validate configuration from YAML."""
    if not path:
        path = Path("config.yaml")
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config(**data)