from json import loads
from traceback import print_exception
from urllib.request import urlopen

import __env__
from dash import dcc, html

from .. import __version__
from ..config import config, imgs

_url_version = "https://pypi.python.org/pypi/SimpleRichTradingJournal/json"
_url_about = "https://raw.githubusercontent.com/Simple-Rich-Trading-Journal/Simple-Rich-Trading-Journal/master/src/SimpleRichTradingJournal/ABOUT.md"
_url_update = (
    "https://raw.githubusercontent.com/Simple-Rich-Trading-Journal/Simple-Rich-Trading-Journal/master/UPDATE.md"
)

_alt_about = __env__._files.proj_root + "/ABOUT.md"

try:
    with urlopen(_url_about) as u:
        about = u.read().decode()
except Exception as e:
    print_exception(e)
    with open(_alt_about) as f:
        about = "*\n\n" + f.read()

update_header = ""
update_note = ""
about_button_color = config.themes.table_bg_main

try:
    with urlopen(_url_version) as u:
        available = loads(u.read())["info"]["version"]
    if __version__ != available:
        about_button_color = config.themes.cell_negvalue
        update_header = f"---\n\n### Version {available} is available!"
        try:
            with urlopen(_url_update) as u:
                update_note = u.read().decode()
        except Exception as e:
            print_exception(e)
    else:
        about_button_color = config.themes.cell_posvalue
except Exception as e:
    print_exception(e)
    update_note = f"An error occurred during the version query: **{e}**"

about = about.format(version=__version__, update_header=update_header, update_note=update_note)


about_button = html.Button(
    imgs.information,
    id="info_button_",
    n_clicks=0,
    style={
        "display": "inline-block",
        "margin": "7px",
        "fontSize": "12px",
        "color": config.themes.table_fg_header,
        "backgroundColor": about_button_color,
        "border": "1px solid " + config.themes.table_sep,
        "paddingLeft": "10px",
        "paddingRight": "10px",
        "borderRadius": "15px",
        "opacity": 0.7,
    },
)


MODAL = html.Div(
    html.Div(
        dcc.Markdown(
            about,
            style={
                "padding": "10px",
                "width": "100%",
            },
            link_target="_blank",
        ),
    ),
    id="about_modal_",
    style={
        "position": "absolute",
        "zIndex": -2,
        "width": 500,
        "top": 50,
        "bottom": 10,
        "left": "calc(50% - 250px)",
        "backgroundColor": config.themes.table_bg_2,
        "color": config.themes.table_fg_main,
        "padding": 10,
        "borderRadius": 10,
        "overflow": "scroll",
    },
)

COMPONENTS = MODAL
