from dash import Dash, html, callback, Output, Input
from dash_ag_grid import AgGrid
import dash
from logprise import logger
from .config.models import Config
from .storage.repository import SQLAlchemyRepository
from .ui.layouts import LAYOUT
from .core.calc import Calc

def run_app(config: Config):
    """Initialize and run Dash app."""
    logger.configure(
        handlers=[{"sink": "srtj.log", "rotation": f"{config.logging.rotation_mb} MB", "retention": f"{config.logging.retention_days} days"}]
    )
    repo = SQLAlchemyRepository(config)

    app = Dash(__name__, title=config.app.host, debug=config.app.debug)
    app.layout = LAYOUT(config, repo)

    # Consolidated callback example (reduce bloat: one for updates)
    @callback(
        Output("logElement", "rowData"),
        Input("update_interval_trigger", "n_clicks"),
        # States for filters, page, etc.
    )
    def update_log(n_clicks, filters, page):
        trades, total = repo.query_trades(filters, page, config.ui.pagination.per_page)
        # Format for view: e.g., holdtime = durationformat((t.take_time - t.invest_time).total_seconds() / 86400, config) if t.take_time else None
        formatted = [
            {
                **t.to_dict(),
                "holdtime": durationformat(...) if ... else None,  # View layer
                "profit": Calc.calculate_profit(t),  # Pure func
            }
            for t in trades
        ]
        return formatted

    # More callbacks: scopes, search, etc., thin wrappers on repo/Calc
    # E.g., for metrics footer:
    @callback(Output("footer", "children"), Input("logElement", "rowData"))
    def update_footer(row_data):
        trades = [Trade(**r) for r in row_data]  # From formatted back to model
        metrics = Calc.calculate_metrics(trades, config=config)
        # Format numbers for view: f"{metrics.summary_value:,.2f}"
        return html.Div(f"Total: {metrics.summary_value:,.2f}")  # Replicate footer

    app.run(host=config.app.host, port=config.app.port, debug=config.app.debug)