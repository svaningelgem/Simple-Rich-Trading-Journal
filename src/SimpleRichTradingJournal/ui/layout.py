from dash import html, dcc
from dash_ag_grid import AgGrid
from typing import Dict
from ..config.models import Config
from ..core.calc import LogCalc
from ..storage.repository import Repository
from .components import make_header, make_balance, make_statistics, make_note, make_footer
from logprise import logger

def create_log_grid(config: Config, lc: LogCalc, repo: Repository) -> AgGrid:
    column_defs = []  # Build from config.ui.log.col_order_asset, widths
    # Example from original [11]
    column_defs.append({
        "field": "InvestTime",
        "headerName": "Time",
        "filter": "agDateColumnFilter",
        "width": config.ui.col_widths[9],
        "type": "rightAligned"
    })
    # Full from log.py [11]
    for i in range(len(config.ui.col_widths)):
        if config.ui.col_widths[i] > 0:
            # Map to fields
            pass

    grid_opts = {
        "rowModelType": "clientSide",  # For now, full load; serverSide for large
        "undoRedoCellEditing": True,
        "undoRedoCellEditingLimit": 20,
        "tabToNextCell": {"function": "tabToNextCell(params)"},
        "dataTypeDefinitions": {},  # From original
        "quickFilterText": "",
    }
    return AgGrid(
        id="logElement",
        columnDefs=column_defs,
        rowData=[t.to_dict() for t in lc.trades],  # Initial
        dashGridOptions=grid_opts,
        getRowId="params.data.id",
        className=config.ui.themes.table.table_theme + " ag-alt-colors",
        style={"height": "100%", "width": "100%", "fontSize": "13px"},
        dangerously_allow_code=True
    )

def create_layout(config: Config, lc: LogCalc, repo: Repository) -> html.Div:
    # Replicate original __init__.py [1]
    tradinglog = create_log_grid(config, lc, repo)
    header_comp = make_header(config)
    balance_comp = make_balance(config, lc) if config.ui.balance.side_init_balance_value else html.Div(style={"display": "none"})
    statistics_comp = make_statistics(config, lc)
    note_comp = make_note(config)
    footer_comp = make_footer(lc, config)
    modal_comp = html.Div([  # From modal.py [12]
        html.Div(style={"position": "absolute", "top": 0, "bottom": 0, "left": 0, "right": 0, "zIndex": -3}),
        html.Button("X", id="close_button", style={"position": "absolute", "left": 20, "top": 20, "zIndex": -3})
    ])
    # Grid layout from [1]
    grid_r1 = html.Div([tradinglog], id="gridR1")
    c1 = html.Div([tradinglog], id="gridC1", className="col-div col-div-flex border-div", style={"width": config.ui.c1_width, "height": "100%"})
    # Full layout assembly
    layout = html.Div([
        html.Div(id="bottomBar", style={"position": "absolute", "bottom": config.ui.bottom_bar_distance_bottom, "right": config.ui.bottom_bar_distance_right, "width": "100%", "zIndex": 1, "display": "none"}),
        html.Div(id="gridR3"),  # Summary footer
        c1,
        # Split handle, etc.
        balance_comp,
        statistics_comp,
        note_comp,
        footer_comp,
        modal_comp,
        dcc.Store(id="init_done_trigger"),
        dcc.Interval(id="update_interval_trigger", interval=5000, n_intervals=0),  # For auto update
    ], id="main")
    return layout