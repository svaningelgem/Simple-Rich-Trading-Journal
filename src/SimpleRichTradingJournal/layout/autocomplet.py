from dash import html, dcc

import __env__

from SimpleRichTradingJournal.config import config

autocdropdown = dcc.Dropdown(
    id="autoCDropdown",
    style={
        "position": "absolute",
        "zIndex": -3,
        "width": 280,

    },
    optionHeight=20,
    maxHeight=config.ui.grid.row3_height,
    className="autocdropdown"
)

autoctrigger = dcc.Input(id="autoCTrigger", style={"display": "none"})

COMPONENTS = html.Div([
    autocdropdown,
    autoctrigger
])
