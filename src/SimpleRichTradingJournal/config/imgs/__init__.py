import base64
from pathlib import Path

from dash import html

here = __path__[0]


def _html_img(src):
    asset = Path(__file__).parent.resolve() / f"../../things/assets/{src}"

    data = b"data:image/png;base64," + base64.b64encode(asset.read_bytes())

    return html.Img(
        src=data,
        style={
            "height": 11
        }
    )


cross = _html_img("cross.png")
information = _html_img("information.png")
refresh = _html_img("refresh.png")
stats = _html_img("stats.png")
