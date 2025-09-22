from typing import List, Dict, Any, Generator
from datetime import datetime
from dataclasses import dataclass
from .utils import prevent_zero_div, durationformat, build_balance_records
from ..storage.models import Trade
from ..config.models import Config
from logprise import logger

@dataclass
class Metrics:
    n_trades_open: int = 0
    n_trades_fin: int = 0
    sum_open_invest: float = 0.0
    sum_fin_invest: float = 0.0
    sum_profits: float = 0.0
    current_performance_on_portfolio: float = 0.0
    dripping_performance_avg: float = 0.0
    summary_value: float = 0.0
    current_summary_rate: float = 0.0
    sum_deposits: float = 0.0
    sum_payouts: float = 0.0
    money: float = 0.0
    n_frame_deposits: int = 0
    n_frame_payouts: int = 0
    # Add all from original LogCalc

class LogCalc:
    """Replicate original LogCalc as class with pure methods."""

    def __init__(self, trades: List[Trade], config: Config):
        self.trades = trades
        self.config = config
        self._deposits = []
        self._payouts = []
        self._fin_trades = []
        self._open_trades = []
        self._undefined = []
        self._dividends = []
        self._itcs = []
        self._calc_all()

    def _calc_all(self):
        """Classify and calc, replicate __f_init_data__."""
        def categorize(trade: Trade, *cats):
            cat = trade.cat
            if cat == "d":
                self._deposits.append(trade)
            elif cat == "p":
                self._payouts.append(trade)
            elif cat == "tf":
                self._fin_trades.append(trade)
            elif cat == "to":
                self._open_trades.append(trade)
            elif cat == "i":
                self._itcs.append(trade)
            elif cat == "v":
                self._dividends.append(trade)
            else:
                self._undefined.append(trade)

        for trade in self.trades:
            categorize(trade)

        self._deposits.sort(key=lambda t: t.invest_time)
        self._payouts.sort(key=lambda t: t.invest_time)
        self._fin_trades.sort(key=lambda t: t.invest_time)
        self._open_trades.sort(key=lambda t: t.invest_time)
        self._undefined.sort(key=lambda t: t.invest_time)
        self._dividends.sort(key=lambda t: t.invest_time)
        self._itcs.sort(key=lambda t: t.invest_time)

        self._calculate_metrics()

    def _calculate_metrics(self):
        """Replicate __f_calc__ and props."""
        self.n_trades_open = len(self._open_trades)
        self.n_trades_fin = len(self._fin_trades)
        self.sum_open_invest = sum(t.invest_amount for t in self._open_trades)
        self.sum_fin_invest = sum(t.invest_amount for t in self._fin_trades)
        self.sum_profits = sum((t.take_amount or 0) - t.invest_amount for t in self._fin_trades)
        self.current_performance_on_portfolio = prevent_zero_div(self.sum_profits, self.sum_fin_invest, 0.0)
        self.dripping_performance_avg = self.current_performance_on_portfolio  # Placeholder, expand
        self.summary_value = self.sum_fin_invest + self.sum_profits
        self.current_summary_rate = prevent_zero_div(self.summary_value - self.sum_fin_invest, self.sum_fin_invest, 0.0)
        self.sum_deposits = sum(t.invest_amount for t in self._deposits)
        self.sum_payouts = sum(abs(t.invest_amount) for t in self._payouts)
        self.money = self.sum_deposits - self.sum_payouts
        self.n_frame_deposits = len(self._deposits)
        self.n_frame_payouts = len(self._payouts)
        # Add full from original, e.g., portfolio_age_sec = (now - first.invest_time).seconds

    def update_course(self) -> List[Trade]:
        """Replicate update_course, generator."""
        for trade in self.trades:
            if trade.cat == "to":
                # Plugin hook if config.storage.plugin
                if self.config.storage.plugin:
                    # Call custom course_call
                    pass
            yield trade

    def get_trade_frame(self, start: datetime, end: datetime) -> 'LogCalc':
        """Frame for performance."""
        filtered = [t for t in self.trades if start <= datetime_from_tradetimeformat(t.invest_time) <= end]
        return LogCalc(filtered, self.config)

    @property
    def first_record(self):
        return self.trades[0] if self.trades else None

    @property
    def last_record(self):
        return self.trades[-1] if self.trades else None

    def __f_reset_calc__(self):
        """Reset for recalc."""
        self._calculate_metrics()

    # Replicate all props and methods from original [11], [7], [16]