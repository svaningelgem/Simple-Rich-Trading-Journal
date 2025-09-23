from datetime import datetime

import __env__


def make_history_list(history: list[tuple[int, int]]):
    return [{"value": v, "label": datetime.fromtimestamp(l).strftime(__env__.config.ui.time_format_history)} for v, l in history]
