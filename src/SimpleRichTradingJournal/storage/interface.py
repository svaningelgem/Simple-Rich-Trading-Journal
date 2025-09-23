# Extract just the StorageInterface abstract class from the first artifact
from abc import ABC, abstractmethod
from typing import Any

from .config import StorageConfig


class StorageInterface(ABC):
    """Abstract interface for trading journal storage"""

    def __init__(self, config: StorageConfig) -> None:
        self.config = config

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage backend"""

    @abstractmethod
    def save_journal(self, data: list[dict[str, Any]]) -> None:
        """Save journal data"""

    @abstractmethod
    def load_journal(self) -> list[dict[str, Any]]:
        """Load journal data"""

    @abstractmethod
    def save_history(self, data: dict[int, dict[str, Any]]) -> None:
        """Save history data"""

    @abstractmethod
    def load_history(self) -> dict[int, dict[str, Any]]:
        """Load history data"""

    @abstractmethod
    def save_column_state(self, data: list[dict[str, Any]] | None) -> None:
        """Save column state data"""

    @abstractmethod
    def load_column_state(self) -> list[dict[str, Any]] | None:
        """Load column state data"""

    @abstractmethod
    def save_position_colors(self, data: dict[str, str]) -> None:
        """Save position color cache"""

    @abstractmethod
    def load_position_colors(self) -> dict[str, str]:
        """Load position color cache"""

    @abstractmethod
    def backup_exists(self) -> bool:
        """Check if backup data exists"""

    @abstractmethod
    def create_backup(self, slot_id: int, timestamp: int, data: list[dict[str, Any]]) -> None:
        """Create a backup entry"""

    @abstractmethod
    def close(self) -> None:
        """Close storage connection"""
