import __env__

from .. import config

modal_close = {"border": "1px solid " + config.themes.table_sep, "backgroundColor": config.themes.top_onoff_bg, "borderRadius": 25, "height": 50}

term_button = {"border": "1px solid " + config.themes.table_sep, "backgroundColor": config.themes.top_onoff_bg, "borderRadius": 25}

by_taketime_on = {"color": config.themes.table_fg_header, "border": "1px solid " + config.themes.table_sep, "backgroundColor": config.themes.col_take, "backgroundImage": ""}
by_taketime_off = by_taketime_on | {"backgroundColor": config.themes.col_invest}

by_index_off = by_taketime_on | {"backgroundColor": config.themes.table_bg_main, "backgroundImage": config.themes.top_by_index_off}

with_open_on = {"color": config.themes.table_fg_main, "border": "1px solid " + config.themes.table_sep, "backgroundColor": config.themes.record_opentrade}
with_open_off = by_taketime_on | {"color": config.themes.table_fg_header, "backgroundColor": config.themes.table_bg_main}

autosave_on = {"color": config.themes.top_onoff_fg, "border": "1px solid " + config.themes.table_sep, "backgroundColor": config.themes.top_onoff_bg}
autosave_off = {"color": config.themes.table_fg_header, "border": "1px solid " + config.themes.table_sep, "backgroundColor": ""}

group_by_options_off = {"color": config.themes.table_fg_main, "border": "1px solid " + config.themes.table_sep, "backgroundColor": config.themes.table_bg_main}
group_by_options_on = group_by_options_off | {"backgroundColor": config.themes.top_onoff_bg}
framing_options_off = {"color": config.themes.table_fg_main, "border": "1px solid " + config.themes.table_sep, "backgroundColor": config.themes.table_bg_main}
framing_options_on = framing_options_off | {"backgroundColor": config.themes.top_onoff_bg}
performance_size = {}

interval_on = {"color": config.themes.top_onoff_fg, "border": "1px solid " + config.themes.table_sep, "backgroundColor": config.themes.top_onoff_bg}
interval_off = {"color": config.themes.table_fg_header, "border": "1px solid " + config.themes.table_sep, "backgroundColor": ""}

summary_footer = {"color": config.themes.table_fg_main, "backgroundColor": config.themes.table_bg_header}
summary_error = {"borderTop": "5px solid " + config.themes.mark_error}
summary_error_reset = {"borderTop": ""}

statistics_button = {
    "color": config.themes.table_fg_main,
    "backgroundColor": config.themes.table_bg_main,
    "border": "1px solid " + config.themes.statistics_button_border,
    "boxShadow": config.themes.statistics_button_shadow + " 0px 3px 10px",
}
balance_button = {
    "color": config.themes.table_fg_main,
    "backgroundColor": config.themes.table_bg_main,
    "border": "1px solid " + config.themes.balance_button_border,
    "boxShadow": config.themes.balance_button_shadow + " 0px 3px 10px",
}
statistics_split_handle = {
    "border": "1px solid " + config.themes.statistics_button_border,
    "boxShadow": config.themes.statistics_button_shadow + " 0px 3px 10px",
    "width": "4px",
}
balance_split_handle = {
    "border": "1px solid " + config.themes.balance_button_border,
    "boxShadow": config.themes.balance_button_shadow + " 0px 3px 10px",
    "width": "4px",
}

header = {"borderBottom": "1px solid " + config.themes.table_sep}
