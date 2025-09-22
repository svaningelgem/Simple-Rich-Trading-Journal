# Extract just the StorageInterface abstract class from the first artifact
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from .config import StorageConfig


class StorageInterface(ABC):
    """Abstract interface for trading journal storage"""

    def __init__(self, config: StorageConfig):
        self.config = config

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage backend"""

    @abstractmethod
    def save_journal(self, data: List[Dict[str, Any]]) -> None:
        """Save journal data"""

    @abstractmethod
    def load_journal(self) -> List[Dict[str, Any]]:
        """Load journal data"""

    @abstractmethod
    def save_history(self, data: Dict[int, Dict[str, Any]]) -> None:
        """Save history data"""

    @abstractmethod
    def load_history(self) -> Dict[int, Dict[str, Any]]:
        """Load history data"""

    @abstractmethod
    def save_column_state(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """Save column state data"""

    @abstractmethod
    def load_column_state(self) -> Optional[List[Dict[str, Any]]]:
        """Load column state data"""

    @abstractmethod
    def save_position_colors(self, data: Dict[str, str]) -> None:
        """Save position color cache"""

    @abstractmethod
    def load_position_colors(self) -> Dict[str, str]:
        """Load position color cache"""

    @abstractmethod
    def backup_exists(self) -> bool:
        """Check if backup data exists"""

    @abstractmethod
    def create_backup(
        self, slot_id: int, timestamp: int, data: List[Dict[str, Any]]
    ) -> None:
        """Create a backup entry"""

    @abstractmethod
    def close(self) -> None:
        """Close storage connection"""
