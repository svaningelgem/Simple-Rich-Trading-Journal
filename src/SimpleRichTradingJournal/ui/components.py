from dash import html, dcc
from ..config.models import Config

def make_button(id: str, text: str, config: Config) -> html.Button:
    """Factory for buttons with theme."""
    return html.Button(
        text,
        id=id,
        style={
            "backgroundColor": config.ui.themes.cell.posvalue or "green",
            "color": config.ui.themes.table.fg_main,
        }
    )

# More factories for checklists, inputs, etc., to reduce repetition