from datetime import datetime, timedelta
from typing import Optional, Callable
from collections import OrderedDict
from ..config.models import Config
from ..storage.models import Trade, LogCalc  # Assume LogCalc in core
from logprise import logger

def durationformat(seconds: float, config: Config) -> str:
    """Format seconds to duration string for UI."""
    duration = int(seconds)
    y = duration // 31557600
    duration %= 31557600
    m = duration // 2629800
    duration %= 2629800
    d = duration // 86400
    duration %= 86400
    h = duration // 3600
    duration %= 3600
    mm = duration // 60
    return f"{y} | {m:02d} | {d:02d} | {h:02d} , {mm}"

def prevent_zero_div(numerator: float, denominator: float, default: Optional[float] = None) -> Optional[float]:
    """Safe division."""
    return numerator / denominator if denominator != 0 else default

def datetime_from_tradetimeformat(spec: str, default: Optional[datetime] = None, config: Config = None) -> Optional[datetime]:
    """Parse trade time string."""
    if not spec:
        return default
    try:
        return datetime.strptime(spec, config.ui.time_format_transaction if config else "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        logger.warning("utils/parse-time-fail: {}", spec)
        return default

def do_add_row(table_data: List[Dict[str, Any]]) -> bool:
    """Validate row addition, replicate original."""
    if not table_data:
        return True
    row0 = table_data[0]
    n = row0.get("n", 0)
    if n < 0:
        return True
    if row0.get("InvestTime") and (row0.get("InvestAmount") or row0.get("InvestCourse") or row0.get("ITC")):
        return True
    if row0.get("TakeTime") and (row0.get("TakeAmount") is not None or row0.get("TakeCourse") is not None or row0.get("ITC")):
        return True
    return False

# Balance records map, replicate _records_def
def build_balance_records(config: Config) -> OrderedDict[str, Callable[[Any], Any]]:
    records = OrderedDict()
    records["DEPOSITS"] = lambda lc: lc.n_frame_deposits
    records["\u200b"] = lambda lc: f"{lc.sum_deposits:,.2f}"
    # Add all from original [7]
    records["PAYOUTS"] = lambda lc: lc.n_frame_payouts
    records["\u200b\u200b"] = lambda lc: f"{lc.sum_payouts:,.2f}"
    # ... full from context
    return records