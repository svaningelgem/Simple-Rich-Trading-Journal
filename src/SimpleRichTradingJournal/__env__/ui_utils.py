"""UI utilities and helpers."""

from logprise import logger

from . import _files
from .loader import config
from .path_manager import paths


class UIUtils:
    """UI-related utilities."""

    def __init__(self):
        self._footer_signal_idx = 0

    def get_footer_live_signal(self) -> dict:
        """Get alternating footer signal for UI updates."""
        if config.startup.disable_footer_life_signal:
            return {}

        self._footer_signal_idx += 1
        if self._footer_signal_idx % 2:
            return {"borderTop": f"1px solid {config.themes.footer.sig2}"}
        return {"borderTop": f"1px solid {config.themes.footer.sig1}"}

    def get_cell_renderer_config(self) -> dict:
        """Get cell renderer configuration."""
        return {
            'take_amount': {"cellRenderer": "agAnimateShowChangeCellRenderer"}
            if config.log.cell_renderer_change.take_amount else {},
            'take_course': {"cellRenderer": "agAnimateShowChangeCellRenderer"}
            if config.log.cell_renderer_change.take_course else {},
            'performance': {"cellRenderer": "agAnimateShowChangeCellRenderer"}
            if config.log.cell_renderer_change.performance else {},
            'profit': {"cellRenderer": "agAnimateShowChangeCellRenderer"}
            if config.log.cell_renderer_change.profit else {},
        }

    def write_pong_file(self, main_pid: int, server_pid: int, profile: str):
        """Write pong file for process management."""
        pong_file = paths.dash_assets.parent / _files.folder_profile_assets / _files.file_pong
        content = f"[{profile}]\nmain    : {main_pid}\nserver  : {server_pid}"
        pong_file.write_text(content)

    def generate_css(self) -> str:
        """Generate dynamic CSS based on theme configuration."""
        css = "/* Auto-generated CSS */\n"

        # Input colors
        css += f"""
.{config.themes.table_theme} input[class^=ag-] {{
    color: {config.themes.main.table_fg_main} !important;
}}
"""

        # Alt colors
        if config.ui.use_default_alt_colors:
            css += f"""
.ag-alt-colors {{
    --ag-value-change-delta-down-color: {config.themes.alt.neg} !important;
    --ag-value-change-delta-up-color: {config.themes.alt.pos} !important;
}}
"""

        # DataTable hover
        css += f"""
.dt-table-container__row-1 .cell-table tbody tr:hover td {{
    background-color: {config.themes.balance.hover_bg} !important;
}}
"""

        # Notepaper links
        css += f"""
.notepaper a {{
    color: {config.themes.notepaper.link} !important;
}}
"""

        # Note editor
        transparency = config.themes.notebook.def_transparency if config.notes.editor_default_transparency else ""
        gutter_transparency = config.themes.notebook.def_gutter_transparency if config.notes.editor_default_transparency else ""

        css += f"""
.CodeMirror {{
    height: 100%;
    width: 100%;
    background-color: {config.themes.notebook.bg}{transparency};
}}
.CodeMirror-gutters {{
    background-color: {config.themes.notebook.gutter_bg}{gutter_transparency};
}}
"""

        # Checkbox styling
        if config.ui.checkbox_long_short_styling and config.ui.checkbox_long_short_styling != "0":
            comment = "//" if config.ui.checkbox_long_short_styling == "s" else ""
            css += f"""
.ag-checkbox-input-wrapper.ag-indeterminate::before {{
    border-width: 0 !important;
}}
.ag-checkbox-input-wrapper.ag-indeterminate::after {{
    color: transparent !important;
}}
.ag-checkbox-input-wrapper.ag-checked::before {{
    border: solid {config.themes.cell_values.neg};
    border-width: 0 3px 3px 0;
    display: inline-block;
    margin: 3px;
    transform: rotate(45deg);
    -webkit-transform: rotate(45deg);
    opacity: 0.5 !important;
}}
.ag-checkbox-input-wrapper.ag-checked::after {{
    color: transparent !important;
}}
.ag-checkbox-input-wrapper::before {{
    {comment}border: solid {config.themes.cell_values.pos};
    border-width: 0 3px 3px 0;
    display: inline-block;
    margin: 3px;
    transform: rotate(-135deg);
    -webkit-transform: rotate(-135deg);
    opacity: 0.5 !important;
}}
.ag-checkbox-input-wrapper::after {{
    color: transparent !important;
}}
.ag-theme-balham, .ag-theme-balham-dark, .ag-theme-balham-auto-dark {{
    --ag-checkbox-border-radius: 10px !important;
    --ag-checkbox-background-color: transparent !important;
}}
"""

        # Row mark
        css += f"""
.row-mark::before {{
    content: "";
    background-color: {config.themes.row_mark};
    display: block;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
}}
"""

        return css


ui_utils = UIUtils()