from __future__ import annotations

from os import kill
from signal import SIGTERM

import __env__
import layout
from dash import Input, Output, State, callback, html

from src.SimpleRichTradingJournal.config import config


@callback(
    Output(layout.exiting.exit_modal_body, "children"),
    Output(layout.exiting_modal_trigger, "n_clicks"),
    Input(layout.exiting.exit_button, "n_clicks"),
    State(layout.exiting_modal_trigger, "n_clicks"),
    config_prevent_initial_callbacks=True,
)
def exiting_req(_, n):
    msg = html.Div(
        html.Table(
            html.Tbody(
                [
                    html.Tr([html.Td("Address\u2007\u2007"), html.Th(f"{config.app.host}:{config.app.port}")]),
                    html.Tr([html.Td("PID\u2007\u2007"), html.Th(f"{__env__.server_manager.server_proc.pid}")]),
                ]
            )
        )
    )
    return msg, n + 1


@callback(
    Output(layout.exiting.exit_modal_button, "children"),
    Input(layout.exiting.exit_modal_button, "n_clicks"),
    config_prevent_initial_callbacks=True,
)
def confirm(_) -> str:
    return "Terminated"


@callback(
    Output(layout.exiting.exit_button, "id"),
    Input(layout.exiting.exit_modal_button, "children"),
    config_prevent_initial_callbacks=True,
)
def exiting(_) -> None:
    kill(__env__.server_manager.server_proc.pid, SIGTERM)
