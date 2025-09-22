from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from logprise import logger
from ..config.models import Config
from ..config.loader import load_config
from .models import Base, TradeTable, History, Trade, HistoryTrades

class Repository(ABC):
    @abstractmethod
    def add_trade(self, trade: Trade) -> None:
        pass

    @abstractmethod
    def query_trades(
            self, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 100, sort_by: str = "invest_time"
    ) -> Tuple[List[Trade], int]:
        pass

    @abstractmethod
    def load_journal(self) -> List[Trade]:
        pass

    @abstractmethod
    def save_history(self, trades: List[Trade], timestamp: datetime) -> int:
        pass

    @abstractmethod
    def load_history(self, history_id: Optional[int] = None) -> Dict[int, Dict[str, Any]]:
        pass

class SQLAlchemyRepository(Repository):
    def __init__(self, config: Config):
        self.engine = create_engine(config.storage.url, echo=config.app.debug)
        SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.session_maker = SessionLocal
        self.config = config
        logger.info("storage/init: url={}", config.storage.url)

    def _get_session(self):
        return self.session_maker()

    def add_trade(self, trade: Trade) -> None:
        session = self._get_session()
        try:
            db_trade = TradeTable(**trade.to_dict())
            session.merge(db_trade)
            session.commit()
            logger.debug("trade/add: id={}", db_trade.id)
        except Exception as e:
            session.rollback()
            logger.error("trade/add-fail: {}", e)
            raise
        finally:
            session.close()

    def query_trades(
            self, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 100, sort_by: str = "invest_time"
    ) -> Tuple[List[Trade], int]:
        session = self._get_session()
        try:
            query = session.query(TradeTable)
            if filters:
                for key, val in filters.items():
                    if key == "cat":
                        query = query.filter(TradeTable.cat == val)
                    elif key == "mark":
                        query = query.filter(TradeTable.mark == 1 if val else 0)
                    # Replicate scopes: e.g., deposits 'd', payouts 'p', etc.
                    elif key == "dividend":
                        query = query.filter(TradeTable.dividend == val)
                    elif key in ["symbol", "name"]:
                        query = query.filter(getattr(TradeTable, key).ilike(f"%{val}%"))
            total = query.count()
            query = query.order_by(text(f"{sort_by} desc")).limit(per_page).offset((page - 1) * per_page)
            db_trades = query.all()
            trades = []
            for db_trade in db_trades:
                trade_dict = {c.name: getattr(db_trade, c.name) for c in db_trade.__table__.columns}
                trades.append(Trade(**trade_dict))
            return trades, total
        finally:
            session.close()

    def load_journal(self) -> List[Trade]:
        _, total = self.query_trades(page=1, per_page=0)  # Get all
        trades, _ = self.query_trades(page=1, per_page=total)
        return trades

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
                history = session.query(History).get(history_id)
                if history:
                    return {history.id: {"time": history.timestamp, "data": history.data}}
                return {}
            histories = session.query(History).order_by(History.timestamp.desc()).all()
            return {h.id: {"time": h.timestamp, "data": h.data} for h in histories}
        finally:
            session.close()