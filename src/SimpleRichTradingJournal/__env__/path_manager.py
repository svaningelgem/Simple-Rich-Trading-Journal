"""Path management for SRTJ."""

from pathlib import Path

from . import _files
from .loader import config
from .profile_manager import profile_manager


class PathManager:
    """Manages all application paths."""

    def __init__(self):
        self._paths = {}
        self.refresh()

    def refresh(self):
        """Refresh all paths based on current profile."""
        profile = profile_manager.profile_folder or Path(_files.default_install_root)

        self._paths = {
            'dash_assets': profile / "files",
            'file_clones': profile / "files" / _files.folder_file_clones,
            'file_clones_url': Path(".") / "files" / _files.folder_file_clones,
            'journal': profile / _files.file_journal,
            'history': profile / _files.file_history,
            'rc_js': profile / "files" / _files.file_rc_js,
            'rc_css': profile / "files" / _files.file_rc_css,
        }

        # Handle conditional paths based on config
        if config.notes.file_drop_cloner == "own":
            self._paths['profile_file_clones'] = profile / _files.folder_profile_assets / _files.folder_file_clones
        else:
            self._paths['profile_file_clones'] = profile_manager.profiles_home / _files.folder_profile_assets / _files.folder_file_clones

        if config.statistics.use_position_color_cache == "own":
            self._paths['color_cache'] = profile / _files.file_position_colors
        else:
            self._paths['color_cache'] = profile_manager.profiles_home / _files.file_position_colors

        if config.log.column_state_cache == "own":
            self._paths['column_cache'] = profile / _files.file_column_state
            self._paths['column_settings'] = profile / _files.file_column_settings
        else:
            self._paths['column_cache'] = profile_manager.profiles_home / _files.file_column_state
            self._paths['column_settings'] = profile_manager.profiles_home / _files.file_column_settings

    def __getattr__(self, name: str) -> Path:
        """Get path by name."""
        if name in self._paths:
            return self._paths[name]
        raise AttributeError(f"Path '{name}' not found")


paths = PathManager()