from datetime import datetime, timedelta
from typing import Optional
from ..config.models import Config

def durationformat(duration: float, config: Config) -> str:
    """Format duration for view layer only."""
    duration = int(duration)
    y = duration // 31557600
    duration %= 31557600
    m = duration // 2629800
    if m or y:
        m = f"0{m:02d}"
    duration %= 2629800
    d = duration // 86400
    if d or m:
        d = f"0{d:02d}"
    duration %= 86400
    h = duration // 3600
    if h or d:
        h = f"0{h:02d}"
    duration %= 3600
    mm = duration // 60
    return f"{y} | {m} | {d} | {h} , {mm}"

def prevent_zero_div(a: float, b: float, default: float) -> float:
    """Prevent division by zero."""
    return a / b if b != 0 else default

def datetime_from_tradetimeformat(spec: str, default: Optional[datetime] = None, config: Config = None) -> Optional[datetime]:
    """Parse datetime for trades."""
    try:
        return datetime.strptime(spec, "%Y-%m-%d %H:%M:%S")  # Replicate __env__.timeFormatTransaction
    except (ValueError, TypeError):
        return default