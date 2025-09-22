from typing import List, Dict, Any, Optional
from .interface import StorageInterface


# Adapter for existing code compatibility
class StorageAdapter:
    """Adapter to maintain compatibility with existing pickle-based code"""

    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.storage.initialize()

    def dump_journal(self, data: List[Dict[str, Any]]) -> None:
        """Compatible with existing dump_journal function"""
        self.storage.save_journal(data)

    def load_journal(self) -> List[Dict[str, Any]]:
        """Compatible with existing journal loading"""
        return self.storage.load_journal()

    def dump_column_state(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """Compatible with existing dump_column_state function"""
        self.storage.save_column_state(data)

    def load_column_state(self) -> Optional[List[Dict[str, Any]]]:
        """Compatible with existing column state loading"""
        return self.storage.load_column_state()

    def dump_position_colors(self, data: Dict[str, str]) -> None:
        """Compatible with existing position color caching"""
        self.storage.save_position_colors(data)

    def load_position_colors(self) -> Dict[str, str]:
        """Compatible with existing position color loading"""
        return self.storage.load_position_colors()

    def close(self) -> None:
        """Close storage connection"""
        self.storage.close()
