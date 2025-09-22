from dash import html, dcc
from dash_ag_grid import AgGrid
from typing import Dict
from ..config.models import Config
from ..storage.repository import Repository

def make_log_grid(config: Config, repo: Repository) -> AgGrid:
    """Create AG-Grid with server-side model for pagination."""
    column_defs = [  # From config.ui.log.col_order/widths
        {"field": "name", "width": config.ui.log.col_widths[0], "headerName": "Name"},
        # ... build dynamically
    ]
    grid_opts = {
        "rowModelType": "serverSide",
        "serverSideStoreType": "partial",
        "cacheBlockSize": config.ui.pagination.per_page,
        "maxBlocksInCache": 10,
        "getRows": lambda params: _get_rows(params, repo, config),  # JS callback to Python via clientside or Input
    }
    return AgGrid(
        id="logElement",
        columnDefs=column_defs,
        dashGridOptions=grid_opts,
        style={"height": "100%", "width": "100%"},
        className=config.ui.themes.table.bg_main,  # Apply themes
    )

def _get_rows(params, repo: Repository, config: Config):
    """Server-side getRows; called via callback."""
    # Translate params.request to filters/sort/page
    page = params.request.startRow // config.ui.pagination.per_page + 1
    filters = {k: v for k, v in params.request.filterModel.items()} if params.request.filterModel else {}
    sort_by = params.request.sortModel[0]["colId"] if params.request.sortModel else "invest_time desc"
    trades, total = repo.query_trades(filters, page, config.ui.pagination.per_page, sort_by)
    # Format view-only
    row_data = [
        {
            **t.to_dict(),
            "invest_time": t.invest_time.strftime("%Y-%m-%d %H:%M") if t.invest_time else "",
            "holdtime": durationformat(...) if ... else "",
        }
        for t in trades
    ]
    params.success({rowData: row_data, rowCount: total})
    return row_data  # For callback return

def LAYOUT(config: Config, repo: Repository) -> html.Div:
    """Main layout with themes applied."""
    return html.Div(
        children=[
            make_log_grid(config, repo),
            html.Div(id="footer"),  # Metrics
            # Balance, stats, note, etc., with config.ui.balance.enabled ? html.Div(...) : None
            dcc.Dropdown(id="scopes", options=[{"label": "Deposits", "value": "d"}]),  # From config
        ],
        style={"backgroundColor": config.ui.themes.table.bg_main},
        id="main-layout"
    )