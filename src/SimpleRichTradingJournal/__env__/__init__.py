"""SRTJ environment initialization."""

from .autoclean import autocleaner
from .cache_manager import color_cache, column_cache
from .data_manager import data_manager
from ..config import config
from .path_manager import paths
from .profile_manager import profile_manager
from .server_manager import server_manager
from .startup import startup
from .ui_utils import ui_utils

# Initialize the application
startup.initialize()

# Export only the new API
__all__ = [
    'config',
    'data_manager',
    'paths',
    'profile_manager',
    'color_cache',
    'column_cache',
    'startup',
    'server_manager',
    'ui_utils',
    'autocleaner',
]