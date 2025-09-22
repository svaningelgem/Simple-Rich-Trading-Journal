# Extract PickleStorage and SQLAlchemyStorage classes from first artifact
from .interface import StorageInterface
from .config import StorageConfig
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import pickle


class PickleStorage(StorageInterface):
    """Pickle-based storage implementation (maintains current behavior)"""

    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.base_path = Path(config.file_path or ".").resolve().absolute()
        self.protocol = pickle.HIGHEST_PROTOCOL

    def initialize(self) -> None:
        """Ensure directories exist"""
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Initialize default files if they don't exist
        files_to_check = [
            ("journal.pkl", []),
            ("history.pkl", {}),
            ("position-colors.pkl", {}),
        ]

        for filename, default_data in files_to_check:
            file_path = self.base_path / filename
            if not file_path.exists():
                self._save_pickle(file_path, default_data)

    def _save_pickle(self, path: Path, data: Any) -> None:
        """Save data to pickle file"""
        with open(path, "wb") as f:
            pickle.dump(data, f, self.protocol)

    def _load_pickle(self, path: Path, default: Any = None) -> Any:
        """Load data from pickle file"""
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return default

    def save_journal(self, data: List[Dict[str, Any]]) -> None:
        self._save_pickle(self.base_path / "journal.pkl", data)

    def load_journal(self) -> List[Dict[str, Any]]:
        return self._load_pickle(self.base_path / "journal.pkl", [])

    def save_history(self, data: Dict[int, Dict[str, Any]]) -> None:
        self._save_pickle(self.base_path / "history.pkl", data)

    def load_history(self) -> Dict[int, Dict[str, Any]]:
        return self._load_pickle(self.base_path / "history.pkl", {})

    def save_column_state(self, data: Optional[List[Dict[str, Any]]]) -> None:
        self._save_pickle(self.base_path / "column-state.pkl", data)

    def load_column_state(self) -> Optional[List[Dict[str, Any]]]:
        return self._load_pickle(self.base_path / "column-state.pkl", None)

    def save_position_colors(self, data: Dict[str, str]) -> None:
        self._save_pickle(self.base_path / "position-colors.pkl", data)

    def load_position_colors(self) -> Dict[str, str]:
        return self._load_pickle(self.base_path / "position-colors.pkl", {})

    def backup_exists(self) -> bool:
        return (self.base_path / "history.pkl").exists()

    def create_backup(
        self, slot_id: int, timestamp: int, data: List[Dict[str, Any]]
    ) -> None:
        # In pickle implementation, this updates the history
        history = self.load_history()
        history[slot_id] = {"time": timestamp, "data": data}
        self.save_history(history)

    def close(self) -> None:
        # Nothing to close for pickle
        pass


class SQLAlchemyStorage(StorageInterface):
    """SQLAlchemy-based storage implementation"""

    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.engine = None
        self.session = None
        self._setup_sqlalchemy()

    def _setup_sqlalchemy(self) -> None:
        """Setup SQLAlchemy engine and models"""
        from sqlalchemy import (
            create_engine,
            Column,
            Integer,
            String,
            DateTime,
            JSON,
        )
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        # Create engine based on backend type
        if self.config.backend == "sqlite":
            db_path = self.config.file_path or "trading_journal.db"
            connection_string = f"sqlite:///{db_path}"
        else:
            connection_string = self.config.connection_string
            if not connection_string:
                raise ValueError(
                    f"Connection string required for {self.config.backend}"
                )

        self.engine = create_engine(connection_string)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Define models
        Base = declarative_base()

        class JournalEntry(Base):
            __tablename__ = f"{self.config.table_prefix}journal"

            id = Column(Integer, primary_key=True)
            data = Column(JSON)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(
                DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
            )

        class HistoryEntry(Base):
            __tablename__ = f"{self.config.table_prefix}history"

            slot_id = Column(Integer, primary_key=True)
            timestamp = Column(Integer)
            data = Column(JSON)
            created_at = Column(DateTime, default=datetime.utcnow)

        class ColumnState(Base):
            __tablename__ = f"{self.config.table_prefix}column_state"

            id = Column(Integer, primary_key=True)
            data = Column(JSON)
            updated_at = Column(
                DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
            )

        class PositionColors(Base):
            __tablename__ = f"{self.config.table_prefix}position_colors"

            key = Column(String(255), primary_key=True)
            color = Column(String(50))
            updated_at = Column(
                DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
            )

        self.models = {
            "JournalEntry": JournalEntry,
            "HistoryEntry": HistoryEntry,
            "ColumnState": ColumnState,
            "PositionColors": PositionColors,
        }

        Base.metadata.create_all(self.engine)

    def initialize(self) -> None:
        """SQLAlchemy initialization is done in __init__"""
        pass

    def save_journal(self, data: List[Dict[str, Any]]) -> None:
        # Clear existing entries and save new data
        self.session.query(self.models["JournalEntry"]).delete()

        for entry in data:
            journal_entry = self.models["JournalEntry"](data=entry)
            self.session.add(journal_entry)

        self.session.commit()

    def load_journal(self) -> List[Dict[str, Any]]:
        entries = (
            self.session.query(self.models["JournalEntry"])
            .order_by(self.models["JournalEntry"].id)
            .all()
        )
        return [entry.data for entry in entries]

    def save_history(self, data: Dict[int, Dict[str, Any]]) -> None:
        # Clear existing and save all history
        self.session.query(self.models["HistoryEntry"]).delete()

        for slot_id, entry in data.items():
            history_entry = self.models["HistoryEntry"](
                slot_id=slot_id, timestamp=entry["time"], data=entry["data"]
            )
            self.session.add(history_entry)

        self.session.commit()

    def load_history(self) -> Dict[int, Dict[str, Any]]:
        entries = self.session.query(self.models["HistoryEntry"]).all()
        return {
            entry.slot_id: {"time": entry.timestamp, "data": entry.data}
            for entry in entries
        }

    def save_column_state(self, data: Optional[List[Dict[str, Any]]]) -> None:
        # Clear existing and save new state
        self.session.query(self.models["ColumnState"]).delete()

        if data is not None:
            column_state = self.models["ColumnState"](data=data)
            self.session.add(column_state)

        self.session.commit()

    def load_column_state(self) -> Optional[List[Dict[str, Any]]]:
        entry = self.session.query(self.models["ColumnState"]).first()
        return entry.data if entry else None

    def save_position_colors(self, data: Dict[str, str]) -> None:
        # Clear existing and save new colors
        self.session.query(self.models["PositionColors"]).delete()

        for key, color in data.items():
            pos_color = self.models["PositionColors"](key=key, color=color)
            self.session.add(pos_color)

        self.session.commit()

    def load_position_colors(self) -> Dict[str, str]:
        entries = self.session.query(self.models["PositionColors"]).all()
        return {entry.key: entry.color for entry in entries}

    def backup_exists(self) -> bool:
        return self.session.query(self.models["HistoryEntry"]).first() is not None

    def create_backup(
        self, slot_id: int, timestamp: int, data: List[Dict[str, Any]]
    ) -> None:
        # Update or create specific history entry
        entry = (
            self.session.query(self.models["HistoryEntry"])
            .filter_by(slot_id=slot_id)
            .first()
        )

        if entry:
            entry.timestamp = timestamp
            entry.data = data
        else:
            entry = self.models["HistoryEntry"](
                slot_id=slot_id, timestamp=timestamp, data=data
            )
            self.session.add(entry)

        self.session.commit()

    def close(self) -> None:
        if self.session:
            self.session.close()
