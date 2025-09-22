from dash import html, dcc
from ..config.models import Config
from ..core.calc import LogCalc

def make_header(config: Config) -> html.Div:
    # Replicate header.py [9]
    scopes_x_func = {
        "\u2007Deposits \u2007\u2007": "params.data.cat == 'd'",
        "\u2007Payouts \u2007\u2007": "params.data.cat == 'p'",
        # Full from original
    }
    _layout = [
        {"value": k, "label": html.Span(k, style={"color": config.ui.themes.table.fg_main})}
        for k in scopes_x_func
    ]
    daterange = dcc.DatePickerRange(
        number_of_months_shown=6,
        day_size=20,
        id="daterange",
        style={"margin": "7px", "fontSize": "13px"}
    )
    index_by_button = html.Button("Index by ...", id="index_by_button", n_clicks=0, style={"margin": "7px", "fontSize": "13px", "padding": "10px", "borderRadius": "15px"})
    scope_by_button = html.Button("Scope by ...", id="scope_by_button", n_clicks=0, style={"margin": "7px", "fontSize": "13px", "padding": "10px", "borderRadius": "15px"})
    with_open_button = html.Button("with open", id="with_open_button", n_clicks=0, style={"margin": "7px", "fontSize": "13px"})
    auto_save_button = html.Button("Auto Save", id="auto_save_button", n_clicks=0)
    return html.Div([
        dcc.Dropdown(id="scopes_check", options=_layout, multi=True, value=[]),
        daterange,
        index_by_button,
        scope_by_button,
        with_open_button,
        auto_save_button,
        html.Input(id="search_input", placeholder="Quick Search", type="text"),
        html.Button("Reset Columns", id="reset_columns_button"),
    ], style={"position": "relative"})

def make_balance(config: Config, lc: LogCalc) -> html.Div:
    # Replicate balance.py [7]
    records = build_balance_records(config)
    content = html.Div([
        html.Div(key + ": " + str(records[key](lc))) for key in records if records[key](lc) is not None
    ], id="balance_content", style={"height": "100%", "overflowY": "scroll"})
    t_button = html.Button("\u2007\u2007T\u2007\u2007", id="T_button", n_clicks=int(config.ui.balance.t52w), style={"display": "inline-block", "margin": "1px"})
    c_button = html.Button("\u2007\u2007~\u2007\u2007", id="C_button", n_clicks=int(config.ui.balance.current), style={"display": "inline-block", "margin": "1px"})
    y_button = html.Button("\u2007\u2007Y\u2007\u2007", id="Y_button", n_clicks=int(config.ui.balance.years), style={"display": "inline-block", "margin": "1px"})
    q_button = html.Button("\u2007\u2007Q\u2007\u2007", id="Q_button", n_clicks=int(config.ui.balance.quarters), style={"display": "inline-block", "margin": "1px"})
    t_trigger = html.Div("", id="T_trigger", n_clicks=int(config.ui.balance.t52w), style={"display": "none"})
    # Similar for others
    balance_buttons = html.Div([t_button, c_button, y_button, q_button, t_trigger], style={"position": "absolute", "zIndex": 1, "fontSize": "8px"})
    return html.Div([
        balance_buttons,
        content
    ], id="balance", style={"height": "100%", "display": "none" if not config.ui.balance.side_init_balance_value else ""})

def make_statistics(config: Config, lc: LogCalc) -> html.Div:
    # Replicate statistics.py [14], performance [16], positions [17]
    # Placeholder graph
    performance_graph = dcc.Graph(id="performance_graph", figure={})  # Build with plotly from lc
    open_positions_graph = dcc.Graph(id="open_positions_graph", figure={})
    all_positions_graph = dcc.Graph(id="all_positions_graph", figure={})
    group_by_checks = [dcc.Checklist(id=f"group_check_{i}", options=[{"label": "L/S", "value": i}], value=config.ui.statistics.group_default[i]) for i in range(5)]
    performance_size_slider = dcc.Slider(id="performance_size_slider", min=1, max=12, value=config.ui.performance.size_slider)
    # Drag container for groups
    drag_container = html.Div(id="drag_container", style={"position": "absolute", "zIndex": -3})
    return html.Div([
        performance_graph,
        open_positions_graph,
        all_positions_graph,
        html.Div(group_by_checks, id="groupBySettings"),
        performance_size_slider,
        drag_container,
        html.Button("Pop Performance", id="pop_performance"),
    ], id="STATISTICS", style={"display": "none"})

def make_note(config: Config) -> html.Div:
    # Replicate note.py [13]
    note_editor = dcc.Textarea(id="noteeditor", style={"width": "100%", "height": "100%"})
    if config.ui.note.mathjax:
        note_editor.children = dcc.Markdown(note_editor.children)
    return html.Div([
        note_editor,
        html.Div(id="notepaperContainer"),
        html.Button("Save Note", id="note_save")
    ], id="note", style={"display": "none"})

def make_footer(lc: LogCalc, config: Config) -> html.Div:
    # Replicate footer.py [15]
    return html.Div([
        html.Table(
            html.Tbody([
                html.Tr([html.Th("Portfolio age"), html.Td(durationformat(lc.portfolio_age_sec, config))]),
                html.Tr([html.Th("Deposits"), html.Td(f"{lc.sum_deposits:,.2f}")]),
                html.Tr([html.Th("Payouts"), html.Td(f"{lc.sum_payouts:,.2f}")]),
                html.Tr([html.Th("Money"), html.Td(f"{lc.money:,.2f}")]),
                html.Tr([html.Th("Positions"), html.Td(lc.n_trades_open), html.Td(lc.n_trades_open + lc.n_trades_fin)]),
                html.Tr([html.Th("Amount"), html.Td(f"{lc.sum_open_invest:,.2f}"), html.Td(f"{lc.sum_open_invest + lc.sum_fin_invest:,.2f}")]),
                html.Tr([html.Th("Profit"), html.Td(f"{lc.sum_profits:,.2f}"), html.Td(f"{lc.current_performance_on_portfolio:,.2%}"), html.Td(f"{lc.dripping_performance_avg:,.2%}")]),
                # Full from original
            ]),
            style={"borderCollapse": "collapse"}
        )
    ], id="summary_footer", style={"verticalAlign": "top", "paddingRight": "5rem"})

def make_about(config: Config) -> html.Div:
    # Replicate about.py [5]
    about_modal = html.Div(
        dcc.Markdown("Simple Rich Trading Journal v0.6.2.1", link_target="_blank"),
        id="about_modal",
        style={"position": "absolute", "zIndex": -2, "width": 500, "top": 50, "backgroundColor": config.ui.themes.table.bg_2, "color": config.ui.themes.table.fg_main, "padding": 10, "borderRadius": 10, "overflow": "scroll"}
    )
    return html.Div([about_modal, html.Button("About", id="about_button")])

# Add make_history, make_exiting from [10], [8]