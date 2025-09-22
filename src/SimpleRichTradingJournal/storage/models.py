from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text, JSON, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

@dataclass
class Trade:
    """Represents a trade record with validation."""
    id: Optional[int] = None
    invest_time: Optional[datetime] = None
    invest_amount: Optional[float] = None
    take_time: Optional[datetime] = None
    take_amount: Optional[float] = None
    name: str = ""
    symbol: str = ""
    isin: str = ""
    type: str = ""
    short: bool = False
    sector: str = ""
    category: str = ""
    rating: Optional[int] = None
    n: int = 1
    invest_course: Optional[float] = None
    take_course: Optional[float] = None
    dividend: bool = False
    itc: Optional[float] = None
    note: str = ""
    hypotheses: str = ""
    mark: bool = False
    cat: str = ""

    def __post_init__(self):
        """Replicate existing validation (do_add_row logic)."""
        if self.n < 0:
            raise ValueError("n cannot be negative")
        if self.invest_time and (self.invest_amount or self.invest_course or self.itc):
            return
        if self.take_time and (self.take_amount is not None or self.take_course is not None or self.itc):
            return
        raise ValueError("Invalid trade data: missing required fields")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class TradeTable(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    invest_time = Column(DateTime, nullable=True)
    invest_amount = Column(Float, nullable=True)
    take_time = Column(DateTime, nullable=True)
    take_amount = Column(Float, nullable=True)
    name = Column(String(255), default="")
    symbol = Column(String(50), default="")
    isin = Column(String(20), default="")
    type = Column(String(50), default="")
    short = Column(Integer, default=0)
    sector = Column(String(100), default="")
    category = Column(String(100), default="")
    rating = Column(Integer, nullable=True)
    n = Column(Integer, default=1)
    invest_course = Column(Float, nullable=True)
    take_course = Column(Float, nullable=True)
    dividend = Column(Integer, default=0)
    itc = Column(Float, nullable=True)
    note = Column(Text, default="")
    hypotheses = Column(Text, default="")
    mark = Column(Integer, default=0)
    cat = Column(String(10), default="")

    __table_args__ = (
        Index("ix_trades_invest_time", invest_time),
        Index("ix_trades_take_time", take_time),
        Index("ix_trades_symbol", symbol),
        Index("ix_trades_name", name),
        Index("ix_trades_cat", cat),
    )

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    data = Column(JSON)  # List of trade dicts as JSON

    trades = relationship("TradeTable", secondary="history_trades", back_populates="histories")

class HistoryTrades(Base):
    __tablename__ = "history_trades"
    history_id = Column(Integer, ForeignKey("history.id"), primary_key=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), primary_key=True)

TradeTable.histories = relationship("History", secondary="history_trades", back_populates="trades")