from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from logprise import logger
from ..config.models import Config
from ..config.loader import load_config
from .models import Base, TradeTable, History, Trade

class Repository(ABC):
    """Abstract interface for storage operations."""

    @abstractmethod
    def add_trade(self, trade: Trade) -> None:
        """Add or update a trade."""

    @abstractmethod
    def query_trades(
            self, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 100, sort_by: str = "invest_time"
    ) -> Tuple[List[Trade], int]:
        """Query trades with pagination and filters."""

    @abstractmethod
    def load_journal(self) -> List[Trade]:
        """Load all trades."""

    @abstractmethod
    def save_history(self, trades: List[Trade], timestamp: datetime) -> int:
        """Save history snapshot."""

    @abstractmethod
    def load_history(self, history_id: Optional[int] = None) -> Dict[int, Dict[str, Any]]:
        """Load history entries."""

class SQLAlchemyRepository(Repository):
    """SQLAlchemy implementation of Repository."""

    def __init__(self, config: Config):
        self.engine = create_engine(config.storage.url, echo=config.app.debug)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)  # Create tables if missing
        self.config = config
        self._load_plugin_if_needed()

    def _load_plugin_if_needed(self):
        plugin_path = self.config.storage.plugin
        if plugin_path:
            # Stub: Load custom repo subclass, e.g., exec(compile(open(plugin_path).read(), plugin_path, 'exec')) or importlib
            logger.warning("plugin/load: {}", plugin_path)
            # For now, assume subclass replaces self if needed; extend via inheritance

    def _get_session(self):
        return self.SessionLocal()

    def add_trade(self, trade: Trade) -> None:
        session = self._get_session()
        try:
            db_trade = TradeTable(**trade.to_dict())
            session.merge(db_trade)  # Update if exists
            session.commit()
            logger.debug("trade/add: id={}", db_trade.id)
        except Exception as e:
            session.rollback()
            logger.error("trade/add-fail: {}", e)
            raise
        finally:
            session.close()

    def query_trades(
            self, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 100, sort_by: str = "invest_time desc"
    ) -> Tuple[List[Trade], int]:
        session = self._get_session()
        try:
            query = session.query(TradeTable)
            if filters:
                # Replicate scopes/quick_search: e.g., if "cat" in filters, query.filter(TradeTable.cat == filters["cat"])
                for key, val in filters.items():
                    if key == "cat":
                        query = query.filter(getattr(TradeTable, key) == val)
                    elif key == "symbol":
                        query = query.filter(TradeTable.symbol.ilike(f"%{val}%"))
                    # Add more as per existing scopes_x_func
            total = query.count()
            query = query.order_by(text(sort_by)).limit(per_page).offset((page - 1) * per_page)
            trades = [Trade(**{c.name: getattr(row, c.name) for c in row.__table__.columns}) for row in query.all()]
            logger.debug("query/trades: page={} count={}", page, len(trades))
            return trades, total
        finally:
            session.close()

    def load_journal(self) -> List[Trade]:
        session = self._get_session()
        try:
            trades = session.query(TradeTable).all()
            return [Trade(**{c.name: getattr(t, c.name) for c in t.__table__.columns}) for t in trades]
        finally:
            session.close()

    def save_history(self, trades: List[Trade], timestamp: datetime) -> int:
        session = self._get_session()
        try:
            history = History(timestamp=timestamp, data=[t.to_dict() for t in trades])
            session.add(history)
            session.commit()
            logger.debug("history/save: id={}", history.id)
            return history.id
        except Exception as e:
            session.rollback()
            logger.error("history/save-fail: {}", e)
            raise
        finally:
            session.close()

    def load_history(self, history_id: Optional[int] = None) -> Dict[int, Dict[str, Any]]:
        session = self._get_session()
        try:
            if history_id:
                hist = session.query(History).get(history_id)
                if hist:
                    return {hist.id: {"time": hist.timestamp, "data": hist.data}}
                return {}
            histories = session.query(History).order_by(History.timestamp.desc()).all()
            return {h.id: {"time": h.timestamp, "data": h.data} for h in histories}
        finally:
            session.close()