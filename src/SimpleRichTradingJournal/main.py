from dash import Dash
from logprise import logger
from .config.models import Config
from .storage.repository import SQLAlchemyRepository
from .ui.layout import create_layout
from .core.calc import LogCalc

def run_app(config: Config):
    repo = SQLAlchemyRepository(config)
    trades = repo.load_journal()
    lc = LogCalc(trades, config)

    app = Dash(__name__, title="Simple Rich Trading Journal", debug=config.app.debug, suppress_callback_exceptions=True)
    app.layout = create_layout(config, lc, repo)

    # Core update callback, replicate courseupdate [21]
    from dash.dependencies import Input, Output, State
    @app.callback(
        Output("logElement", "rowData"),
        Output("summary_footer", "children"),
        Output("balance_content", "children"),
        # Add outputs for graphs, etc.
        Input("update_interval_trigger", "n_clicks"),
        State("scopes_check", "value"),
        State("daterange", "start_date"),
        # ... all states from original
    )
    def update_all(n, scopes, start, end, with_open, size, steps, trailing_frame, trailing_interval, range_, hypothesis_per, drag_style, drag_event, stats_style, balance_style, t_trigger, c_trigger, y_trigger, q_trigger, scope_button, drag_event2, footer_style, group_checks):
        if n is None:
            return dash.no_update, dash.no_update, dash.no_update
        # Update trades from repo
        trades = repo.load_journal()
        lc.trades = list(lc.update_course())
        lc._calc_all()
        # Filter by scopes/dates
        if scopes:
            filters = {"cat": scopes[0]}  # Simplify, expand for multiple
            filtered_trades, _ = repo.query_trades(filters)
            lc = LogCalc(filtered_trades, config)
        # Format rowData for grid
        row_data = [
            {
                **t.to_dict(),
                "HoldTime": durationformat((datetime_from_tradetimeformat(t.take_time) - datetime_from_tradetimeformat(t.invest_time)).total_seconds() if t.take_time else 0, config),
                "Profit": f"{t.take_amount - t.invest_amount:,.2f}" if t.take_amount else "",
                # Format all view fields
            }
            for t in lc.trades
        ]
        # Footer from lc
        footer_children = html.Table(  # Replicate footer [15]
            html.Tbody([
                html.Tr([html.Th("Positions"), html.Td(lc.n_trades_open), html.Td(lc.n_trades_open + lc.n_trades_fin)]),
                # Full table from original
            ])
        )
        # Balance content from records [7]
        records = build_balance_records(config)
        balance_children = html.Div([html.P(key + ": " + records[key](lc)) for key in records])
        return row_data, footer_children, balance_children

    # Add other callbacks: scopes [24], onoff [22], openmodal [23], columnstate [20], autocomplete [18], etc.
    # For example, scopes callback
    @app.callback(
        Output("logElement", "dashGridOptions"),
        Input("scopes_check", "value")
    )
    def update_scopes(scopes):
        if not scopes:
            return {"isExternalFilterPresent": {"function": "false"}, "doesExternalFilterPass": {"function": "true"}}
        filter_func = " || ".join([f"params.data.cat == '{s}'" for s in scopes])
        return {"isExternalFilterPresent": {"function": "true"}, "doesExternalFilterPass": {"function": filter_func}}

    # History callback [10]
    @app.callback(
        Output("history_list", "options"),
        Input("history_modal_trigger", "n_clicks")
    )
    def update_history(n):
        repo = SQLAlchemyRepository(config)  # Global or context
        history = repo.load_history()
        options = [{"label": v["time"].strftime(config.ui.time_format_history), "value": k} for k, v in history.items()]
        return options

    # Run
    if config.app.quiet:
        logger.remove()
    app.run(host=config.app.host, port=config.app.port, debug=config.app.debug, use_reloader=not config.app.administrative)