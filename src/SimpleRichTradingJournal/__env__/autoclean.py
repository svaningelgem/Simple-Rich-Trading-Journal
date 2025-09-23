"""Automatic cleanup operations."""

import pickle
from pathlib import Path
from re import finditer
from time import time
from urllib.parse import unquote

from logprise import logger

from . import _files
from .loader import config
from .path_manager import paths


class AutoCleaner:
    """Handles automatic cleanup of unused files."""

    def run(self, journal_data: list[dict]) -> None:
        """Run autoclean if interval has passed."""
        t = int(time())
        clean_time_file = paths.dash_assets.parent / _files.file_clean_time

        try:
            with open(clean_time_file) as f:
                clean_time = int(f.read())
        except FileNotFoundError:
            clean_time = 0

        remain = (clean_time + config.maintenance.autoclean_interval_s) - t
        if remain > 0:
            return

        with open(clean_time_file, "w") as f:
            f.write(str(t))

        self._clean_file_clones(journal_data)
        self._clean_color_cache(journal_data)

    def _clean_file_clones(self, journal_data: list[dict]):
        """Clean unused file clones."""
        file_clones_dir = paths.file_clones
        if not file_clones_dir.exists():
            return

        fileclones = list(file_clones_dir.iterdir())
        if not fileclones:
            return

        # Find referenced files in notes
        for row in journal_data:
            if note := row.get("Note"):
                for m in finditer(r"(\[[^\]]*\])(\([^\)]+\))", note):
                    link = unquote(m.group(2))
                    fileclones = [f for f in fileclones if f.name != link]

        # Move or delete unreferenced files
        trash_dir = paths.dash_assets.parent / _files.folder_trash
        trash_dir.mkdir(exist_ok=True)

        for old_file in trash_dir.iterdir():
            old_file.unlink()

        for fileclone in fileclones:
            if config.notes.file_drop_cloner_flush_trashing:
                (trash_dir / fileclone.name).write_bytes(fileclone.read_bytes())
            fileclone.unlink()

    def _clean_color_cache(self, journal_data: list[dict]):
        """Clean unused color cache entries."""
        if not config.statistics.use_position_color_cache:
            return

        ids = set()
        id_fields = ("Name", "Symbol", "Type", "Sector", "Category")
        for row in journal_data:
            for field in id_fields:
                if value := row.get(field):
                    ids.add(value)

        try:
            with open(paths.color_cache, "rb") as f:
                old_cache = pickle.load(f)
        except FileNotFoundError:
            return

        new_cache = {k: v for k, v in old_cache.items() if k in ids}

        with open(paths.color_cache, "wb") as f:
            pickle.dump(new_cache, f, config.storage.pickle_protocol)


autocleaner = AutoCleaner()