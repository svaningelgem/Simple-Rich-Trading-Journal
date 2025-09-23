# Extract StorageFactory from first artifact
from typing import Any

from .backends import PickleStorage, SQLAlchemyStorage
from .config import StorageConfig
from .interface import StorageInterface


class StorageFactory:
    """Factory for creating storage instances"""

    _backends = {
        "pickle": PickleStorage,
        "sqlite": SQLAlchemyStorage,
        "mysql": SQLAlchemyStorage,
        "postgresql": SQLAlchemyStorage,
    }

    @classmethod
    def create(cls, config: StorageConfig | dict[str, Any]) -> StorageInterface:
        """Create storage instance based on configuration"""
        if isinstance(config, dict):
            config = StorageConfig.from_dict(config)

        backend_cls = cls._backends.get(config.backend)
        if not backend_cls:
            raise ValueError(f"Unsupported storage backend: {config.backend}")

        return backend_cls(config)

    @classmethod
    def register_backend(cls, name: str, backend_cls: type) -> None:
        """Register a new storage backend"""
        cls._backends[name] = backend_cls
