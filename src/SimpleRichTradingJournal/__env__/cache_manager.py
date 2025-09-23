"""Cache management for colors and columns."""

import pickle
from pathlib import Path
from typing import Any

from logprise import logger

from .loader import config
from .path_manager import paths


class ColorCache:
    """Manages position color caching."""

    def __init__(self):
        self._cache: dict[str, str] = {}
        self._palette = []
        self._load()

    def _load(self):
        """Load color cache from disk."""
        if not config.statistics.use_position_color_cache or config.statistics.use_position_color_cache == "0":
            return

        try:
            with open(paths.color_cache, "rb") as f:
                self._cache = pickle.load(f)
        except FileNotFoundError:
            self._dump()

    def _dump(self):
        """Save color cache to disk."""
        if not config.statistics.use_position_color_cache or config.statistics.use_position_color_cache == "0":
            return

        with open(paths.color_cache, "wb") as f:
            pickle.dump(self._cache, f, config.storage.pickle_protocol)

    def get_position_color(self, key: str) -> str:
        """Get color for a position, assigning new one if needed."""
        if key in self._cache:
            return self._cache[key]

        if not self._palette:
            self._palette = config.themes.color_palette_positions.copy()

        color = self._palette.pop(0)
        self._cache[key] = color
        self._dump()
        return color


class ColumnCache:
    """Manages column state caching."""

    def __init__(self):
        self.data: list[dict] | None = None
        self.ini_state = False
        self._load()

    def _load(self):
        """Load column cache from disk."""
        if not config.log.column_state_cache or config.log.column_state_cache == "0":
            return

        settings_data = [
            config.log.col_order_asset_id,
            config.log.col_order_note,
            config.log.col_order,
            config.log.col_widths,
        ]

        try:
            with open(paths.column_settings, "rb") as f:
                self.ini_state = pickle.load(f) == settings_data
        except FileNotFoundError:
            self.ini_state = False

        with open(paths.column_settings, "wb") as f:
            pickle.dump(settings_data, f, config.storage.pickle_protocol)

        try:
            with open(paths.column_cache, "rb") as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.dump(None)

    def dump(self, data: list[dict] | None):
        """Save column state to disk."""
        self.data = data
        with open(paths.column_cache, "wb") as f:
            pickle.dump(data, f, config.storage.pickle_protocol)


color_cache = ColorCache()
column_cache = ColumnCache()