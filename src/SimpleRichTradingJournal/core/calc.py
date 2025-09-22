from typing import List, NamedTuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from .utils import prevent_zero_div
from ..storage.models import Trade
from ..config.models import Config

@dataclass
class Metrics(NamedTuple):
    n_trades_open: int
    n_trades_fin: int
    sum_open_invest: float
    sum_fin_invest: float
    summary_value: float
    current_summary_rate: float
    # Add more as per LogCalc props

class Calc:
    """Pure calculation functions, no side effects."""

    @staticmethod
    def calculate_metrics(trades: List[Trade], with_open: bool = False, config: Config = None) -> Metrics:
        """Calculate summary metrics from trades."""
        open_trades = [t for t in trades if t.take_time is None]
        fin_trades = [t for t in trades if t.take_time is not None]
        n_open = len(open_trades)
        n_fin = len(fin_trades)
        sum_open = sum(t.invest_amount or 0 for t in open_trades)
        sum_fin = sum(t.invest_amount or 0 for t in fin_trades)
        total_invest = sum_open + sum_fin if with_open else sum_fin
        # Replicate summary logic; placeholder for full perf/profit
        summary_value = total_invest  # Expand with profit calcs
        rate = prevent_zero_div(summary_value - total_invest, total_invest, 0.0)
        return Metrics(n_open, n_fin, sum_open, sum_fin, summary_value, rate)

    @staticmethod
    def update_course(trades: List[Trade], config: Config = None) -> List[Trade]:
        """Update courses if plugin hook applies; generator for efficiency."""
        for trade in trades:
            if trade.cat == "to" and not trade.take_amount:  # Open trade
                # Plugin stub: if config.storage.plugin, call custom course_call
                pass
            yield trade

    # Add more pure funcs, e.g., performance_trailing as staticmethod