"""Data management for journal and history."""

import pickle
from datetime import datetime
from pathlib import Path
from time import time

from logprise import logger

from ..storage import StorageAdapter, StorageFactory
from . import plugin
from .loader import config
from .path_manager import paths


class DataManager:
    """Manages journal and history data."""

    def __init__(self):
        self.journal_data: list[dict] = []
        self.history_data: dict = {}
        self.history_keys_x_time_revsort: list[tuple[int, int]] = []
        self.last_history_creation_time: int = 0
        self.storage_adapter: StorageAdapter | None = None
        self._init_storage()
        self._init_data()

    def _init_storage(self):
        """Initialize storage adapter."""
        storage_config = {
            "backend": config.storage.backend,
            "connection_string": config.storage.connection_string,
            "table_prefix": config.storage.table_prefix,
            "file_path": str(paths.dash_assets.parent),
        }
        self.storage_adapter = StorageAdapter(StorageFactory.create(storage_config))

    def _init_data(self):
        """Initialize journal and history data."""
        first_run = [{
            "id": 0,
            "n": 0,
            "InvestTime": datetime.now().strftime(config.ui.time_format_transaction),
            "InvestAmount": 1
        }]

        t = int(time())

        try:
            with open(paths.journal, "rb") as f:
                self.journal_data = pickle.load(f)
        except FileNotFoundError:
            self.journal_data = first_run
            self.storage_adapter.dump_journal(self.journal_data)

        try:
            with open(paths.history, "rb") as f:
                self.history_data = pickle.load(f)
        except FileNotFoundError:
            self.history_data = {
                i: {"time": i, "data": first_run}
                for i in range(config.maintenance.n_history_slots)
            }

        do_dump = plugin.init_log(self.journal_data)
        make_hist = plugin.init_history(self.history_data)

        self.history_keys_x_time_revsort = [
            (k, v["time"]) for k, v in self.history_data.items()
        ]
        self.history_keys_x_time_revsort.sort(key=lambda x: x[1], reverse=True)

        if do_dump:
            self.storage_adapter.dump_journal(self.journal_data)
            self._make_history(t)
        elif make_hist:
            with open(paths.history, "wb") as f:
                pickle.dump(self.history_data, f, config.storage.pickle_protocol)
        else:
            self._check_history_needed(t)

        self.last_history_creation_time = self.history_data[self.history_keys_x_time_revsort[0][0]]["time"]

    def _make_history(self, t: int):
        """Create a new history entry."""
        self.last_history_creation_time = t
        self.history_data[self.history_keys_x_time_revsort[-1][0]] = {
            "time": self.last_history_creation_time,
            "data": self.journal_data
        }
        with open(paths.history, "wb") as f:
            pickle.dump(self.history_data, f, config.storage.pickle_protocol)

    def _check_history_needed(self, t: int):
        """Check if a new history entry is needed."""
        newest_backup = self.history_data[self.history_keys_x_time_revsort[0][0]]["data"]

        if len(self.journal_data) != len(newest_backup):
            self._make_history(t)
            return

        initdata = self.journal_data.copy()
        initdata.sort(key=lambda x: x["id"])
        newest_backup.sort(key=lambda x: x["id"])
        comp_keys = ("id", "Name", "n", "InvestTime", "InvestAmount",
                     "TakeTime", "TakeAmount", "ITC", "Note")

        for ini, bku in zip(initdata, newest_backup, strict=False):
            if tuple(ini.get(k) for k in comp_keys) != tuple(bku.get(k) for k in comp_keys):
                self._make_history(t)
                return


data_manager = DataManager()