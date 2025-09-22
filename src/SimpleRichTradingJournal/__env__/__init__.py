import pickle
import webbrowser
from argparse import Namespace
from ast import literal_eval
from datetime import datetime
from importlib import util, reload
from multiprocessing import Process
from os import environ, mkdir, symlink, scandir, remove, listdir, system, getpid, kill
from pathlib import Path
from re import finditer, search, DOTALL
from signal import SIGTERM
from time import time
from urllib.parse import unquote
from urllib.request import urlopen

# New config system imports
from config.loader import init_config, get_config
import config.loader as config

import __ini__.cmdl
import __ini__.logtags
from . import plugin, _upgrade, _files
from .rconfig import *
from things import make_assets


def _upgrade_profile(
        profile_path: str,
        rc: bool = False,
        colors: bool = False,
        plugins: bool = False,
        things: bool = False,
):
    print(__ini__.logtags.profile_make, profile_path)
    try:
        mkdir(profile_path)
    except FileExistsError:
        pass

    if rc:
        profile_rc = _files.make_path(profile_path, _files.inactive_prefix + _files.file_rc)
        with open(_files.make_path(_files.env, _files.file_rc)) as _if, open(profile_rc, "w") as _of:
            _of.write(_if.read())

    if colors:
        profile_cc = _files.make_path(profile_path, _files.inactive_prefix + _files.file_cc)
        with open(_files.make_path(_files.env, _files.file_cc)) as _if, open(profile_cc, "w") as _of:
            _of.write(_if.read())

    if plugins:
        profile_plugin = _files.make_path(profile_path, _files.inactive_prefix + _files.file_plugin)
        with open(_files.make_path(_files.env, _files.file_plugin)) as _if, open(profile_plugin, "w") as _of:
            _of.write(_if.read())

    try:
        mkdir(_files.make_path(profile_path, _files.folder_profile_assets))
    except FileExistsError:
        pass
    try:
        mkdir(_files.make_path(profile_path, _files.folder_profile_assets, _files.folder_file_clones))
    except FileExistsError:
        pass
    try:
        mkdir(_files.make_path(profile_path, _files.folder_trash))
    except FileExistsError:
        pass

    with open(_files.make_path(profile_path, _files.file_clean_time), "w") as f:
        f.write(str(int(time())))

    def make_thing():
        symlink(file.path, dst)

    if things:
        def remake_thing():
            remove(dst)
            make_thing()

    else:
        def remake_thing():
            pass

    make_assets()
    for file in scandir(_files.proj_things_assets):
        dst = _files.make_path(profile_path, _files.folder_profile_assets, file.name)
        try:
            make_thing()
        except FileExistsError:
            remake_thing()

    return profile_path


def _make_profile(profile_path: str, force: bool = False):
    print(__ini__.logtags.profile_make, profile_path)
    try:
        mkdir(profile_path)
    except FileExistsError:
        if not force:
            raise

    return _upgrade_profile(profile_path)


def _upgrade_root(profiles_home: str):
    _call_gui = _files.make_path(profiles_home, _files.file_call_gui)
    with open(_files.make_path(_files.env, _files.file_call_gui), "rb") as _if:
        __call_gui = _if.read()
        if Path(_call_gui).exists():
            if input(
                    f"{__ini__.logtags.upgrade} file exists: {_call_gui}\n"
                    f"Overwrite? > "
            ).lower() in ("1", "y", "yes"):
                bu_file = _call_gui + "-srtj-lt0.5-backup.txt"
                print(__ini__.logtags.upgrade, "create backup:", f"{bu_file}")
                with open(bu_file, "wb") as _of:
                    _of.write(__call_gui)
                print(__ini__.logtags.upgrade, "overwrite:", _call_gui)
            else:
                return print(__ini__.logtags.upgrade, "skip:", _call_gui)
        with open(_call_gui, "wb") as _of:
            _of.write(__call_gui)


def _install(profiles_root: str):
    global __profiles_home__
    __profiles_home__ = _files.make_path(profiles_root, _files.profiles_home_folder)
    print(__ini__.logtags.install, "@", __profiles_home__)
    _make_profile(__profiles_home__)

    with open(_files.profiles_home_path_file, "w") as f:
        f.write(__profiles_home__)

    _upgrade_root(__profiles_home__)


def _autoclean(journal_data):
    t = int(time())
    __file_clean_time = _files.make_path(__profile_folder__, _files.file_clean_time)
    print(__ini__.logtags.cleaner, "load:", __file_clean_time)
    with open(__file_clean_time) as __f:
        clean_time = int(__f.read())
    remain = (clean_time + config.maintenance.autoclean_interval_s) - t
    print(__ini__.logtags.cleaner, f"{remain=}s")
    if remain <= 0:
        with open(__file_clean_time, "w") as __f:
            __f.write(str(t))

        journal_datas = [journal_data]

        def scan_for_globals(attr_name, default_is_glob):
            gval = globals()[attr_name]
            print(__ini__.logtags.cleaner, "scan for globals:", attr_name, "is", repr(gval))
            if gval == "global":
                for profile in scandir(__profiles_home__):
                    if profile.name.startswith(_files.profile_prefix):
                        spec = util.spec_from_file_location("", _files.make_path(profile.path, _files.file_rc))
                        _rc = util.module_from_spec(spec)
                        spec.loader.exec_module(_rc)
                        try:
                            is_glob = getattr(_rc, attr_name) == "global"
                        except AttributeError:
                            is_glob = default_is_glob
                        if is_glob:
                            print(__ini__.logtags.cleaner, "scan for globals/add:", profile.name)
                            with open(_files.make_path(__profiles_home__, profile.name), "rb") as f:
                                journal_datas.append(pickle.load(f))

        if fileclones := listdir(FILE_CLONES):
            scan_for_globals(
                f"{noteFileDropCloner=}".split("=")[0],
                noteFileDropCloner == "global"
            )
            for data in journal_datas:
                for row in data:
                    if note := row.get("Note"):
                        for m in finditer("(\\[[^\\]*]\\])(\\([^\\)]+\\))", note):
                            link = unquote(m.group(2))
                            try:
                                fileclones.remove(link)
                            except ValueError:
                                if not fileclones:
                                    break

            if noteFileDropCloner == "global":
                trash = _files.make_path(__profiles_home__, _files.folder_trash)
            else:
                trash = _files.make_path(__profile_folder__, _files.folder_trash)

            print(__ini__.logtags.cleaner, "flush trash @", trash)
            for e in listdir(trash):
                remove(_files.make_path(trash, e))

            if noteFileDropClonerFlushTrashing:
                print(__ini__.logtags.cleaner, "trashing:", fileclones)
                for fileclone in fileclones:
                    with open(path := _files.make_path(FILE_CLONES, fileclone), "rb") as _if:
                        with open(_files.make_path(trash, fileclone), "wb") as _of:
                            _of.write(_if.read())
                    remove(path)
            else:
                print(__ini__.logtags.cleaner, "flushing:", fileclones)
                for fileclone in fileclones:
                    remove(_files.make_path(FILE_CLONES, fileclone))

        journal_datas = [journal_data]
        scan_for_globals(
            f"{statisticsUsePositionColorCache=}".split("=")[0],
            statisticsUsePositionColorCache == "global"
        )
        ids = set()
        id_fields = ("Name", "Symbol", "Type", "Sector", "Category")
        for data in journal_datas:
            for row in data:
                for field in id_fields:
                    ids.add(row.get(field))
        with open(COLOR_CACHE, "rb") as f:
            _color_cache = pickle.load(f)
        color_cache = dict()
        for _id in ids:
            try:
                color_cache[_id] = _color_cache[_id]
            except KeyError:
                pass
        with open(COLOR_CACHE, "wb") as f:
            pickle.dump(color_cache, f)


# Global variables for backward compatibility
PROFILE: str = ""
__profile_folder__: str = ""
storage_adapter = None
_globals = globals()


def _initialize_config() -> None:
    """Initialize configuration system and set up backward compatibility."""
    global storage_adapter

    try:
        # Initialize config with profile folder
        config.init(profile_folder=__profile_folder__ if __profile_folder__ else None)
        print(__ini__.logtags.profile_load, "config loaded successfully")

        # Set up storage adapter
        from ..storage import StorageFactory, StorageAdapter
        storage_config = {
            'backend': config.storage.backend,
            'connection_string': config.storage.connection_string,
            'table_prefix': config.storage.table_prefix,
            'file_path': __profile_folder__ or _files.default_install_root
        }
        storage_adapter = StorageAdapter(StorageFactory.create(storage_config))
    except Exception as e:
        print(__ini__.logtags.error, f"Config initialization failed: {e}")
        raise


def _load_profile(profile):
    global __profile_folder__, PROFILE
    if profile:
        PROFILE = profile
        __profile_folder__ = _files.make_path(__profiles_home__, _files.profile_prefix + profile)
        print(__ini__.logtags.profile_load, profile, "@", __profile_folder__)
    else:
        __profile_folder__ = __profiles_home__
    if not Path(__profile_folder__).exists():
        _make_profile(__profile_folder__)

    # Load legacy RC files if they exist
    if (p := Path(_files.make_path(__profile_folder__, _files.file_rc))).exists():
        print(__ini__.logtags.profile_load, p)
        spec = util.spec_from_file_location("rc", p)
        _rc = util.module_from_spec(spec)
        spec.loader.exec_module(_rc)
        for attr in _rc.__dir__():
            if attr.startswith("_"):
                continue
            _globals[attr] = getattr(_rc, attr)

    if (p := Path(_files.make_path(__profile_folder__, _files.file_plugin))).exists():
        print(__ini__.logtags.profile_load, p)
        spec = util.spec_from_file_location("plugin", p)
        _plugin = util.module_from_spec(spec)
        spec.loader.exec_module(_plugin)
        for attr in _plugin.__dir__():
            if attr.startswith("_"):
                continue
            setattr(plugin, attr, getattr(_plugin, attr))


def _cmdline():
    if __ini__.cmdl.DIRECTIVES:
        if len(__ini__.cmdl.DIRECTIVES) == 1:
            _load_profile(__ini__.cmdl.DIRECTIVES[0])
        else:
            print(__ini__.logtags.cmdl, "parse:", __ini__.cmdl.DIRECTIVES)
            _config_key = __ini__.cmdl.DIRECTIVES.pop(0)
            if _config_key == "/":
                _load_profile(__ini__.cmdl.DIRECTIVES.pop(0))
                if __ini__.cmdl.DIRECTIVES:
                    _config_key = __ini__.cmdl.DIRECTIVES.pop(0)
            while __ini__.cmdl.DIRECTIVES:
                if _config_key.endswith("]"):
                    _config_key, _idx = _config_key[:-1].split("[")
                    _attr = getattr(rconfig, _config_key)
                    _attr.__setitem__(int(_idx), type(_attr[0])(__ini__.cmdl.DIRECTIVES.pop(0)))
                elif (_attrt := type(_attr := getattr(rconfig, _config_key))) is list:
                    _arg = __ini__.cmdl.DIRECTIVES.pop(0)
                    if not _arg.startswith("["):
                        raise ValueError(f"{_config_key!r} requires a value of type <list> whose pattern corresponds to [1, 2, ...]. {_arg!r} is received.")
                    while not _arg.endswith("]"):
                        _arg += __ini__.cmdl.DIRECTIVES.pop(0)
                    _globals[_config_key] = literal_eval(_arg)
                else:
                    _globals[_config_key] = _attrt(__ini__.cmdl.DIRECTIVES.pop(0))
                try:
                    _config_key = __ini__.cmdl.DIRECTIVES.pop(0)
                except IndexError:
                    break


def _profile_list() -> list[str]:
    return [n for e in scandir(__profiles_home__) if (n := e.name).startswith(_files.profile_prefix)]


# Initialize installation and profiles
try:
    if __ini__.cmdl.DIRECTIVES[0] == "install":
        __ini__.cmdl.DIRECTIVES.pop(0)
        try:
            _install(__ini__.cmdl.DIRECTIVES[0])
            __ini__.cmdl.DIRECTIVES.pop(0)
        except IndexError:
            _install(_files.default_install_root)
except IndexError:
    pass

try:
    with open(_files.profiles_home_path_file) as _f:
        __profiles_home__ = _f.read().strip()
        if not Path(__profiles_home__).exists():
            raise FileNotFoundError
except FileNotFoundError:
    _install(_files.default_install_root)

# Handle upgrade commands
try:
    if __ini__.cmdl.DIRECTIVES[0] == "upgrade":
        __ini__.cmdl.DIRECTIVES.pop(0)
        if __ini__.cmdl.DIRECTIVES and __ini__.cmdl.DIRECTIVES[0] == "all":
            __env = Namespace(**globals())
            _upgrade.call(__profiles_home__, __env)
            _upgrade_profile(__profiles_home__, True, True, True, True)
            for p in _profile_list():
                __profile = _files.make_path(__profiles_home__, p)
                _upgrade.call(__profile, __env)
                _upgrade_profile(__profile, True, True, True, True)
            _upgrade_root(__profiles_home__)
            exit()
        elif __ini__.cmdl.DIRECTIVES and __ini__.cmdl.DIRECTIVES[0] == "/":
            _profile_folder = _files.make_path(__profiles_home__, _files.profile_prefix + __ini__.cmdl.DIRECTIVES[1])
        else:
            _profile_folder = __profiles_home__
        if __ini__.cmdl.DIRECTIVES:
            rc = colors = plugins = things = False
            try:
                rc = __ini__.cmdl.DIRECTIVES.remove("rc")
            except ValueError:
                pass
            try:
                colors = __ini__.cmdl.DIRECTIVES.remove("colors")
            except ValueError:
                pass
            try:
                plugins = __ini__.cmdl.DIRECTIVES.remove("plugins")
            except ValueError:
                pass
            try:
                things = __ini__.cmdl.DIRECTIVES.remove("things")
            except ValueError:
                pass
        else:
            rc = colors = plugins = things = True
        _upgrade_profile(_profile_folder, rc, colors, plugins, things)
        exit()
    elif __ini__.cmdl.DIRECTIVES[0] == "help":
        with open(rconfig.__file__) as f:
            print(str().join(f.read().splitlines(keepends=True)[1:]))
        exit()
    elif __ini__.cmdl.DIRECTIVES[0] == "version":
        from SimpleRichTradingJournal import __version__
        exit(__version__)
except IndexError:
    pass

# Load profile and initialize config
_load_profile(None)
try:
    _load_profile(environ["SRTJ"])
except KeyError:
    pass
_cmdline()

# Initialize configuration system
from ..config import config
_initialize_config()

# Set up URL and other path-dependent variables
URL = f"http://{config.app.host}:{config.app.port}"
PONG_URL = _files.make_path(URL, _files.folder_profile_assets, _files.file_pong)


def make_pong_file(server_pid):
    with open(_files.make_path(__profile_folder__, _files.folder_profile_assets, _files.file_pong), "w") as f:
        f.write(f"[{PROFILE}]\n"
                f"main    : {getpid()}\n"
                f"server  : {server_pid}")


def ping() -> bytes | bool:
    try:
        with urlopen(PONG_URL) as u:
            return u.read()
    except:
        return False


def _kill():
    if __ping := ping():
        ___ping = __ping.splitlines()[1:]
        __main = int(___ping[0].split(b':')[1].strip())
        __server = int(___ping[1].split(b':')[1].strip())
        kill(__server, SIGTERM)
        kill(__main, SIGTERM)
        return __ping
    else:
        return False


if __ini__.cmdl.FLAGS.ping:
    if __ping := ping():
        print(__ping.decode())
        exit()
    else:
        print(__ini__.logtags.ping_fail, PONG_URL)
        exit(1)

elif __ini__.cmdl.FLAGS.kill:
    if __ping := _kill():
        print(__ini__.logtags.kill, __ping.decode())
        exit()
    else:
        print(__ini__.logtags.ping_fail, PONG_URL)
        exit(1)

# Set up path variables based on config
DASH_ASSETS = _files.make_path(__profile_folder__, "files")
FILE_CLONES = _files.make_path(DASH_ASSETS, _files.folder_file_clones)
FILE_CLONES_URL = _files.make_path(".", "files", _files.folder_file_clones)

if config.notes.file_drop_cloner == "own":
    PROFILE_FILE_CLONES = _files.make_path(__profile_folder__, _files.folder_profile_assets, _files.folder_file_clones)
else:
    PROFILE_FILE_CLONES = _files.make_path(__profiles_home__, _files.folder_profile_assets, _files.folder_file_clones)

if config.statistics.use_position_color_cache == "own":
    COLOR_CACHE = _files.make_path(__profile_folder__, _files.file_position_colors)
else:
    COLOR_CACHE = _files.make_path(__profiles_home__, _files.file_position_colors)

if config.log.column_state_cache == "own":
    COLUMN_CACHE = _files.make_path(__profile_folder__, _files.file_column_state)
    COLUMN_SETTINGS = _files.make_path(__profile_folder__, _files.file_column_settings)
else:
    COLUMN_CACHE = _files.make_path(__profiles_home__, _files.file_column_state)
    COLUMN_SETTINGS = _files.make_path(__profiles_home__, _files.file_column_settings)

# Set up date/time formats
dateFormat = {"ISO 8601": "ydm", "american": "mdy", "international": "dmy"}.get(config.ui.date_format, config.ui.date_format)
timeFormatTransaction, timeFormatHistory, timeFormatDaterange, timeFormatLastCalc = {
    "ydm": ("%y/%d/%m %H:%M", "\u2007\u2007%a. %y/%d/%m %H:%M.%S", "YY/DD/MM", "%y / %d / %m"),
    "mdy": ("%m/%d/%y %H:%M", "\u2007\u2007%a. %m/%d/%y %H:%M.%S", "MM/DD/YY", "%m / %d / %y"),
    "dmy": ("%d/%m/%y %H:%M", "\u2007\u2007%a. %d/%m/%y %H:%M.%S", "DD/MM/YY", "%d / %m / %y"),
}[dateFormat]

# Write JavaScript config file
with open(_files.make_path(DASH_ASSETS, _files.file_rc_js), "w") as f:
    f.write(
        "// [do not change] this file is created by `rc'\n"
        f"const gridDefWidthScale={config.ui.grid.def_width_scale};"
        f"const gridMinWidthScale={config.ui.grid.min_width_scale};"
        f"const gridRow3Height={config.ui.grid.row3_height};"
        f"const dateFormat={dateFormat!r};"
        f"const ccCopy = {config.ui.bind_key_codes[0]!r};"
        f"const ccCut = {config.ui.bind_key_codes[1]!r};"
        f"const ccPaste = {config.ui.bind_key_codes[2]!r};"
        f"const ccCopyRow1 = {config.ui.bind_key_codes[3]!r};"
        f"const ccCopyRow2 = {config.ui.bind_key_codes[4]!r};"
        f"const ccCopyRow3 = {config.ui.bind_key_codes[5]!r};"
        f"const ccAComplete = {config.ui.bind_key_codes[6]!r};"
        f"const ccNote = {config.ui.bind_key_codes[7]!r};"
        f"const ccNoteBack = {config.ui.bind_key_codes[8]!r};"
        f"const ccMark = {config.ui.bind_key_codes[9]!r};"
        f"const noteCellVariableFormatter={int(config.notes.cell_variable_formatter)};"
        f"const noteUnifying={int(config.notes.unifying)};"
        f"const noteLinkDropPattern=/{config.notes.link_drop_pattern}/;"
        f"const notePathDropPattern=/{config.notes.path_drop_pattern}/;"
    )

# Set up statistics grouping
if config.statistics.id_by_symbol:
    statisticsGroupId = "Symbol"
else:
    statisticsGroupId = "Name"

# # Set up grid sizing
# TODO --> move to config
# if config.ui.grid.side_size_init_scale:
#     gridSideSizeInitValue = int(config.ui.grid.side_size_init_scale * 100)
#     c2Width = f"{gridSideSizeInitValue}%"
#     c1Width = f"{100 - gridSideSizeInitValue}%"
#     sideInitStatisticValue = int(not config.ui.grid.side_init_balance)
# else:
#     gridSideSizeInitValue = 0
#     c2Width = "0%"
#     c1Width = "100%"
#     sideInitStatisticValue = 0

# Set up position color cache
_colorCache = dict()
if config.statistics.use_position_color_cache and config.statistics.use_position_color_cache != '0':
    def _dump_color_cache():
        with open(COLOR_CACHE, "wb") as __f:
            pickle.dump(_colorCache, __f)

    try:
        with open(COLOR_CACHE, "rb") as __f:
            _colorCache = pickle.load(__f)
    except FileNotFoundError:
        _dump_color_cache()
else:
    def _dump_color_cache():
        pass

_colorPalette = config.themes.color_palette_positions.copy()


def get_position_color(__key):
    global _colorPalette
    try:
        return _colorCache[__key]
    except KeyError:
        try:
            color = _colorPalette.pop(0)
        except IndexError:
            _colorPalette = config.themes.color_palette_positions.copy()
            color = _colorPalette.pop(0)
        _colorCache[__key] = color
        _dump_color_cache()
        return color


# Column state management
COLUMN_CACHE_DATA: list[dict] | None = None


def dump_column_state(data):
    global COLUMN_CACHE_DATA
    COLUMN_CACHE_DATA = data
    with open(COLUMN_CACHE, "wb") as __f:
        pickle.dump(data, __f)


# Initialize column state cache
# TODO --> This should not be saved in a pickle file, but in the database.
if columnStateCache := (config.log.column_state_cache and config.log.column_state_cache != '0' and not __ini__.cmdl.FLAGS.debug):
    _column_settings_data = [
        config.log.col_order_asset_id,
        config.log.col_order_note,
        config.log.col_order,
        config.log.col_widths,
    ]
    try:
        with open(COLUMN_SETTINGS, "rb") as __f:
            iniColumnState = pickle.load(__f) == _column_settings_data
    except FileNotFoundError:
        iniColumnState = False
    with open(COLUMN_SETTINGS, "wb") as __f:
        pickle.dump(_column_settings_data, __f)
    try:
        with open(COLUMN_CACHE, "rb") as __f:
            COLUMN_CACHE_DATA = pickle.load(__f)
    except FileNotFoundError:
        dump_column_state(None)

# Set up cell renderers
cellRendererChangeTakeAmount = ({"cellRenderer": "agAnimateShowChangeCellRenderer"} if config.log.cell_renderer_change.take_amount else {})
cellRendererChangeTakeCourse = ({"cellRenderer": "agAnimateShowChangeCellRenderer"} if config.log.cell_renderer_change.take_course else {})
cellRendererChangePerformance = ({"cellRenderer": "agAnimateShowChangeCellRenderer"} if config.log.cell_renderer_change.performance else {})
cellRendererChangeProfit = ({"cellRenderer": "agAnimateShowChangeCellRenderer"} if config.log.cell_renderer_change.profit else {})

nStatisticsDrag = len(set(config.statistics.performance.order))

# Write CSS file
with open(_files.make_path(DASH_ASSETS, _files.file_rc_css), "w") as f:
    cont = "/* [do not change] this file is created by `rc' */\n"
    cont += """
/* agGrid Input color > */
.%s input[class^=ag-] {
  color: %s !important;
}
/* < agGrid Input color */
""" % (config.themes.table_theme, config.themes.main.table_fg_main)

    if config.ui.use_default_alt_colors:
        cont += """
/* agGrid alt colors > */
.ag-alt-colors {
    --ag-value-change-delta-down-color: %s !important;
    --ag-value-change-delta-up-color: %s !important;
}
/* < agGrid alt colors */
""" % (config.themes.alt.neg, config.themes.alt.pos)

    cont += """
/* dataTable hover bg > */
.dt-table-container__row-1 .cell-table tbody tr:hover td {
  background-color: %s !important;
}
/* < dataTable hover bg */
""" % config.themes.balance.hover_bg

    cont += """
/* notepaper > */
.notepaper a {
  color: %s !important;
}
/* < notepaper */
""" % config.themes.notepaper.link

    cont += """
/* note editor > */
.CodeMirror {
  height: 100%%;
  width: 100%%;
  background-color: %s;
}
.CodeMirror-gutters {
  background-color: %s;
}
/* < note editor */
""" % (
        config.themes.notebook.bg + (config.themes.notebook.def_transparency if config.notes.editor_default_transparency else ""),
        config.themes.notebook.gutter_bg + (config.themes.notebook.def_gutter_transparency if config.notes.editor_default_transparency else ""),
    )

    if config.ui.checkbox_long_short_styling and config.ui.checkbox_long_short_styling != '0':
        cont += """
/* Short > */
.ag-checkbox-input-wrapper.ag-indeterminate::before {
  border-width: 0 !important;
}
.ag-checkbox-input-wrapper.ag-indeterminate::after {
  color: transparent !important;
}
.ag-checkbox-input-wrapper.ag-checked::before {
  border: solid %s;
  border-width: 0 3px 3px 0;
  display: inline-block;
  margin: 3px;
  transform: rotate(45deg);
  -webkit-transform: rotate(45deg);
  opacity: 0.5 !important;
}
.ag-checkbox-input-wrapper.ag-checked::after {
  color: transparent !important;
}
.ag-checkbox-input-wrapper::before {
 %s border: solid %s;
  border-width: 0 3px 3px 0;
  display: inline-block;
  margin: 3px;
  transform: rotate(-135deg);
  -webkit-transform: rotate(-135deg);
  opacity: 0.5 !important;
}
.ag-checkbox-input-wrapper::after {
  color: transparent !important;
}
.ag-theme-balham, .ag-theme-balham-dark, .ag-theme-balham-auto-dark {
  --ag-checkbox-border-radius: 10px !important;
  --ag-checkbox-background-color: transparent !important;
}
/* < Short */
""" % (config.themes.cell_values.neg, ("//" if config.ui.checkbox_long_short_styling == "s" else ""), config.themes.cell_values.pos)

    cont += """
/* Row Mark > */
.row-mark::before {
  content: "";
  background-color: %s;
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}
/* < Row Mark */
""" % config.themes.row_mark
    f.write(cont)

# Footer live signal
_idx = 0

def get_footer_live_signal():
    global _idx
    _idx += 1
    if _idx % 2:
        return {"borderTop": "1px solid " + config.themes.footer.sig2}
    else:
        return {"borderTop": "1px solid " + config.themes.footer.sig1}

_d = dict()

if config.startup.disable_footer_life_signal:
    def get_footer_live_signal():
        return _d

# Scope settings
if config.scope.strict_scope_by_both:
    scope_by_both = "or+"
else:
    scope_by_both = "or"

# Data initialization
JOURNAL_DATA: list[dict] = list()
HISTORY_DATA: dict = dict()
HISTORY_KEYS_X_TIME_REVSORT: list[tuple[int, int]] = list()
LAST_HISTORY_CREATION_TIME: int = 0

JOURNAL = _files.make_path(__profile_folder__, _files.file_journal)
HISTORY = _files.make_path(__profile_folder__, _files.file_history)

pickleProtocol = config.storage.pickle_protocol

def _init_data():
    global JOURNAL_DATA, HISTORY_DATA, HISTORY_KEYS_X_TIME_REVSORT, LAST_HISTORY_CREATION_TIME
    __firstrun = [{"id": 0, "n": 0, "InvestTime": datetime.now().strftime(timeFormatTransaction), "InvestAmount": 1}]
    t = int(time())
    try:
        print(__ini__.logtags.profile_init, "journal/load:", JOURNAL)
        with open(JOURNAL, "rb") as __f:
            JOURNAL_DATA = pickle.load(__f)
    except FileNotFoundError:
        print(__ini__.logtags.profile_init, "journal/first run:", __firstrun)
        JOURNAL_DATA = __firstrun
        storage_adapter.dump_journal(JOURNAL_DATA)
    try:
        print(__ini__.logtags.profile_init, "history/load:", HISTORY)
        with open(HISTORY, "rb") as __f:
            HISTORY_DATA = pickle.load(__f)
    except FileNotFoundError:
        print(__ini__.logtags.profile_init, "history/first run:", __firstrun)
        HISTORY_DATA = {i: {"time": i, "data": __firstrun} for i in range(config.maintenance.n_history_slots)}

    print(__ini__.logtags.profile_init, "plugin/call")
    do_dump = plugin.init_log(JOURNAL_DATA)
    make_hist = plugin.init_history(HISTORY_DATA)

    HISTORY_KEYS_X_TIME_REVSORT = list((k, v["time"]) for k, v in HISTORY_DATA.items())
    HISTORY_KEYS_X_TIME_REVSORT.sort(key=lambda x: x[1], reverse=True)

    def make_history():
        global LAST_HISTORY_CREATION_TIME
        LAST_HISTORY_CREATION_TIME = t
        HISTORY_DATA[HISTORY_KEYS_X_TIME_REVSORT[-1][0]] = {"time": LAST_HISTORY_CREATION_TIME, "data": JOURNAL_DATA}
        with open(HISTORY, "wb") as __f:
            pickle.dump(HISTORY_DATA, __f, pickleProtocol)

    if do_dump:
        print(__ini__.logtags.profile_init, "plugin/journal -> dump")
        storage_adapter.dump_journal(JOURNAL_DATA)
        make_history()
    elif make_hist:
        print(__ini__.logtags.profile_init, "plugin/history -> dump")
        with open(HISTORY, "wb") as __f:
            pickle.dump(HISTORY_DATA, __f, pickleProtocol)
    else:
        newest_backup = HISTORY_DATA[HISTORY_KEYS_X_TIME_REVSORT[0][0]]["data"]

        if len(JOURNAL_DATA) != len(newest_backup):
            print(__ini__.logtags.profile_init, "history/n-entries -> create+dump")
            make_history()
            return

        initdata = JOURNAL_DATA.copy()
        initdata.sort(key=lambda x: x["id"])
        newest_backup.sort(key=lambda x: x["id"])
        comp_keys = ("id", "Name", "n", "InvestTime", "InvestAmount", "TakeTime", "TakeAmount", "ITC", "Note")

        for ini, bku in zip(initdata, newest_backup):
            if tuple(ini.get(k) for k in comp_keys) != tuple(bku.get(k) for k in comp_keys):
                print(__ini__.logtags.profile_init, "history/cell-contents -> create+dump")
                make_history()
                return

        print(__ini__.logtags.profile_init, "history -> no changes")

    LAST_HISTORY_CREATION_TIME = HISTORY_DATA[HISTORY_KEYS_X_TIME_REVSORT[0][0]]["time"]

    return JOURNAL_DATA

if config.plugins.quick_disable:
    reload(plugin)

_init_data()
_autoclean(JOURNAL_DATA)

SERVER_PROC: Process

CALL_GUI = lambda: None


def _parse_call_gui():
    global CALL_GUI
    with open(_files.make_path(__profiles_home__, _files.file_call_gui)) as f:
        content = f.read()

    if start_section := search(
            "(?:(?:\n|^)\\[start])(((?!\n\\[).)*)", content, DOTALL
    ):
        proc = None
        for line in start_section.group(1).splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                proc = line
                break

        if proc == "*none":
            return
        elif proc == "*pop":
            def CALL_GUI():
                dwb = webbrowser.get()
                print(__ini__.logtags.call_gui, "*pop using:", URL, "->", dwb.name, dwb.args, flush=True)
                webbrowser.open_new_tab(URL)

            CALL_GUI = CALL_GUI
        elif proc:
            if params_section := search(
                    f"(?:(?:\n|^)\\[start\\.{proc}\\.params])(((?!\n\\[).)*)", content, DOTALL
            ):
                for line in params_section.group(1).splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        proc += f" {line}"

                proc = proc.format(
                    **(
                            globals()
                            | {
                                "*url": URL,
                                "*profile-root": __profile_folder__,
                                "*user-home": Path.home().__str__()
                            }
                    ),
                )

            else:
                proc += f" {URL}"

            def CALL_GUI():
                print(__ini__.logtags.call_gui, "using:", proc, flush=True)
                system(proc)

            CALL_GUI = CALL_GUI


_parse_call_gui()
#
#
# def __getattr__(name):
#     """Provide backward compatibility for old-style config access."""
#     cfg = get_config()
#
#     # Map old names to new config paths
#     mappings = {
#         'dateFormat': lambda: config.ui.date_format,
#         'columnStateCache': lambda: config.log.column_state_cache,
#         'statisticsUsePositionColorCache': lambda: config.statistics.use_position_color_cache,
#         'noteFileDropCloner': lambda: config.notes.file_drop_cloner,
#         'noteFileDropClonerFlushTrashing': lambda: config.notes.file_drop_cloner_flush_trashing,
#     }
#
#     if name in mappings:
#         return mappings[name]()
#
#     # Check if it's a theme attribute
#     if hasattr(config.themes, name):
#         return getattr(config.themes, name)
#
#     # Check nested theme attributes
#     for section_name in ['main', 'alt', 'columns', 'records', 'cell_values', 'marks', 'figures', 'footer', 'topbar', 'balance', 'notepaper', 'notebook', 'noteeditor_dialog']:
#         if hasattr(getattr(config.themes, section_name, None), name):
#             return getattr(getattr(config.themes, section_name), name)
#
#     # Handle color_theme backward compatibility
#     if name == 'color_theme':
#         return config.themes
#
#     raise AttributeError(f"module '{__name__}' has no attribute '{name}'")