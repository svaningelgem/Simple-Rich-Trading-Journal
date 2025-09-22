from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Any, List
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text, Boolean, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

@dataclass
class Trade:
    id: Optional[int] = field(default=None, repr=False)
    cat: str = ""
    mark: int = 0
    name: str = ""
    symbol: str = ""
    isin: str = ""
    type: str = ""
    short: bool = False
    sector: str = ""
    category: str = ""
    rating: Optional[float] = None
    n: float = 0
    invest_time: str = ""  # Stored as string to match original, parse in utils
    invest_amount: float = 0
    invest_course: float = 0
    take_time: str = ""
    take_amount: Optional[float] = None
    take_course: Optional[float] = None
    itc: Optional[float] = None
    dividend: bool = False
    note: str = ""
    hypotheses: str = ""

    def __post_init__(self):
        if self.n < 0:
            raise ValueError("n must be non-negative")
        if self.invest_time and not (self.invest_amount or self.invest_course or self.itc):
            raise ValueError("Invest time requires amount, course, or ITC")
        if self.take_time and self.take_amount is None and self.take_course is None and self.itc is None:
            raise ValueError("Take time requires amount, course, or ITC")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["mark"] = 1 if d["mark"] else 0
        d["short"] = True if d["short"] else False
        d["dividend"] = True if d["dividend"] else False
        return d

class TradeTable(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cat = Column(String(10), default="")
    mark = Column(Integer, default=0)
    name = Column(String(255), default="")
    symbol = Column(String(50), default="")
    isin = Column(String(20), default="")
    type = Column(String(50), default="")
    short = Column(Boolean, default=False)
    sector = Column(String(100), default="")
    category = Column(String(100), default="")
    rating = Column(Float, nullable=True)
    n = Column(Float, default=0)
    invest_time = Column(String(50), nullable=True)
    invest_amount = Column(Float, default=0)
    invest_course = Column(Float, default=0)
    take_time = Column(String(50), nullable=True)
    take_amount = Column(Float, nullable=True)
    take_course = Column(Float, nullable=True)
    itc = Column(Float, nullable=True)
    dividend = Column(Boolean, default=False)
    note = Column(Text, default="")
    hypotheses = Column(Text, default="")

    __table_args__ = (
        Index("ix_trades_invest_time", invest_time),
        Index("ix_trades_take_time", take_time),
        Index("ix_trades_symbol", symbol),
        Index("ix_trades_name", name),
        Index("ix_trades_cat", cat),
        Index("ix_trades_mark", mark),
    )

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)
    data = Column(JSON)  # List of trade dicts

    trades = relationship("TradeTable", secondary="history_trades")

class HistoryTrades(Base):
    __tablename__ = "history_trades"
    history_id = Column(Integer, ForeignKey("history.id"), primary_key=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), primary_key=True)