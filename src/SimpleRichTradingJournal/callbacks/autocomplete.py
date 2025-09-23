from json import loads

import layout
from callbacks import main
from dash import Input, Output, callback, no_update


@callback(
    Output(layout.autocomplet.autocdropdown, "options"),
    Input(layout.autocomplet.autocdropdown, "search_value"),
    Input(layout.autocomplet.autoctrigger, "value"),
    config_prevent_initial_callbacks=True,
)
def autoc_enter(search_val, trigger):
    trigger = loads(trigger)
    match trigger["_col"]:
        case "Name":
            opts = main.__lc__.__mainFrame__._names
        case "Symbol":
            opts = main.__lc__.__mainFrame__._symbols
        case "ISIN":
            opts = main.__lc__.__mainFrame__._isins
        case "Type":
            opts = main.__lc__.__mainFrame__._types
        case "Sector":
            opts = main.__lc__.__mainFrame__._sectors
        case "Category":
            opts = main.__lc__.__mainFrame__._categories
        case _:
            return no_update

    return [{"label": i, "value": i} for i in opts]
