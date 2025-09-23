"""Pydantic models for SRTJ configuration."""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class AppConfig(BaseModel):
    """Application-level configuration."""

    host: str = "127.0.0.1"
    port: int = Field(default=8050, ge=1024, le=65535)
    profile: str = ""
    @property
    def url(self) -> str:
        """Server URL"""
        return f"http://{self.host}:{self.port}"

    @property
    def pong_url(self) -> str:
        """Pong endpoint URL"""
        return f"{self.url}/files/.pong"

class StartupConfig(BaseModel):
    """Startup behavior configuration."""

    flush_open_take_amount: bool = True
    disable_copy_paste: bool = False
    disable_footer_life_signal: bool = True


class GridConfig(BaseModel):
    """Grid layout configuration."""

    side_init_balance: bool = False
    side_size_init_scale: float = Field(default=0.2, ge=0.0, le=1.0)
    def_width_scale: float = Field(default=0.2, ge=0.0, le=1.0)
    min_width_scale: float = Field(default=0.1, ge=0.0, le=1.0)
    row3_height: int = Field(default=120, ge=50)
    bottom_bar_distance_bottom: int = Field(default=105, ge=0)
    bottom_bar_distance_right: int = Field(default=10, ge=0)

    @property
    def side_init_balance_value(self):
        if self.side_size_init_scale:
            return self.side_init_balance
        return 0


# # Set up grid sizing
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


class UIConfig(BaseModel):
    """User interface configuration."""

    date_format: Literal["ISO 8601", "american", "international", "ydm", "mdy", "dmy"] = "international"
    date_format_first_day_of_week: int = Field(default=1, ge=0, le=6)
    color_theme: Literal["dark", "light", "blank"] = "dark"
    use_default_alt_colors: bool = False
    checkbox_long_short_styling: Literal["", "0", "s", "ls"] = "s"
    grid: GridConfig = Field(default_factory=GridConfig)
    bind_key_codes: list[str] = Field(
        default_factory=lambda: ["KeyC", "KeyX", "KeyV", "KeyA", "KeyY", "KeyZ", "Space", "KeyI", "Backslash", "KeyM"]
    )

    @field_validator("bind_key_codes")
    @classmethod
    def validate_key_codes(cls, v):
        if len(v) != 10:
            raise ValueError("bind_key_codes must have exactly 10 elements")
        return v

    # Date/time formatting computed properties
    @property
    def date_format_code(self) -> str:
        """Get internal date format code"""
        return {"ISO 8601": "ydm", "american": "mdy", "international": "dmy"}.get(
            self.date_format, self.date_format
        )

    @property
    def time_format_transaction(self) -> str:
        formats = {
            "ydm": "%y/%d/%m %H:%M",
            "mdy": "%m/%d/%y %H:%M",
            "dmy": "%d/%m/%y %H:%M"
        }
        return formats[self.date_format_code]

    @property
    def time_format_history(self) -> str:
        formats = {
            "ydm": "\u2007\u2007%a. %y/%d/%m %H:%M.%S",
            "mdy": "\u2007\u2007%a. %m/%d/%y %H:%M.%S",
            "dmy": "\u2007\u2007%a. %d/%m/%y %H:%M.%S"
        }
        return formats[self.date_format_code]

    @property
    def time_format_daterange(self) -> str:
        formats = {"ydm": "YY/DD/MM", "mdy": "MM/DD/YY", "dmy": "DD/MM/YY"}
        return formats[self.date_format_code]

    @property
    def time_format_last_calc(self) -> str:
        formats = {"ydm": "%y / %d / %m", "mdy": "%m / %d / %y", "dmy": "%d / %m / %y"}
        return formats[self.date_format_code]

class ScopeConfig(BaseModel):
    """Data scoping configuration."""

    index_by_take_time: bool = False
    scope_by_index: bool = True
    strict_scope_by_both: bool = True
    calc_with_opens: bool = True

    @property
    def scope_by_both_mode(self) -> str:
        """Scope by both mode string"""
        return "or+" if self.strict_scope_by_both else "or"

class CellRendererChangeConfig(BaseModel):
    """Cell renderer change animation configuration."""

    take_amount: bool = False
    take_course: bool = False
    performance: bool = True
    profit: bool = True


class LogConfig(BaseModel):
    """Journal log configuration."""

    col_order_asset_id: list[int] = Field(default_factory=lambda: [-1, 1, 2, 3, 4, 5, 6, 7, 8])
    col_order_note: list[int] = Field(default_factory=lambda: [0, 0, 0, 0, 0, 0, 0, 8])
    col_order: list[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5, 6, 7, 8])
    col_widths: list[int] = Field(
        default_factory=lambda: [
            140,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            80,
            170,
            150,
            110,
            170,
            150,
            110,
            80,
            110,
            110,
            80,
            120,
            170,
            160,
            160,
            160,
            160,
        ]
    )
    column_state_cache: Literal["", "0", "global", "own"] = "global"
    cell_renderer_change: CellRendererChangeConfig = Field(default_factory=CellRendererChangeConfig)

    @field_validator("col_widths")
    @classmethod
    def validate_col_widths(cls, v):
        if len(v) != 25:
            raise ValueError("col_widths must have exactly 25 elements")
        return v


class BalanceConfig(BaseModel):
    """Balance section configuration."""

    t52w: bool = True
    current: bool = True
    years: bool = True
    quarters: bool = True


class PerformanceConfig(BaseModel):
    """Performance analysis configuration."""

    steps_default: Literal["w", "m", "q"] = "w"
    interval_default: Literal["w", "m", "q"] = "w"
    frame_default: Literal["w", "m", "q"] = "q"
    range_default: Literal[0, 12, 24, 48] = 0
    hypothesis_per_day: bool = False
    order: list[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5, 6, 7, 8])

    @field_validator("order")
    @classmethod
    def validate_order(cls, v):
        if len(v) != 8:
            raise ValueError("order must have exactly 8 elements")
        if set(v) != set(range(1, 9)):
            raise ValueError("order must contain unique values 1-8")
        return v


class GraphSizesConfig(BaseModel):
    """Graph size configuration."""

    performance: int = Field(default=1000, ge=500, le=6000)
    pop: int = Field(default=2000, ge=500, le=6000)
    open_positions: int = Field(default=500, ge=200, le=2000)
    all_positions: int = Field(default=500, ge=200, le=2000)


class StatisticsConfig(BaseModel):
    """Statistics configuration."""

    group_default: list[int] = Field(default_factory=lambda: [0, 0, 0, 0, 1])
    sun_max_depth: int = Field(default=4, ge=1)
    use_sun_max_depth: bool = True
    id_by_symbol: bool = False
    use_position_color_cache: Literal["", "0", "global", "own"] = "global"
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    graph_sizes: GraphSizesConfig = Field(default_factory=GraphSizesConfig)

    @field_validator("group_default")
    @classmethod
    def validate_group_default(cls, v):
        if len(v) != 5:
            raise ValueError("group_default must have exactly 5 elements")
        return v
    @property
    def group_id_field(self) -> str:
        """Field to use for statistics grouping"""
        return "Symbol" if self.id_by_symbol else "Name"

    @property
    def n_statistics_drag(self) -> int:
        """Number of draggable statistics sections"""
        return len(set(self.performance.order))

class NotesConfig(BaseModel):
    """Notes interface configuration."""

    paper_default_transparency: bool = True
    editor_default_transparency: bool = True
    file_drop_cloner: Literal["", "0", "global", "own"] = "global"
    file_drop_cloner_img_alt_name: bool = False
    link_drop_pattern: str = "^(https?:\\/\\/|www\\.)"
    path_drop_pattern: str = "^(\\/|[A-Z]:\\\\)"
    file_drop_cloner_flush_trashing: bool = True
    mathjax: bool = False
    cell_variable_formatter: bool = True
    mathjax_masker: bool = True
    unifying: bool = True


class PluginsConfig(BaseModel):
    """Plugin configuration."""

    course_update_interval: bool = False
    course_update_interval_on: bool = False
    course_update_interval_ms: int = Field(default=10000, ge=1000)
    quick_disable: bool = False


class StorageConfig(BaseModel):
    """Storage backend configuration."""

    backend: Literal["pickle", "sqlite", "mysql", "postgresql"] = "pickle"
    connection_string: str = ""
    table_prefix: str = "srtj_"
    pickle_protocol: int = Field(default=5, ge=0, le=5)


class MaintenanceConfig(BaseModel):
    """Maintenance and cleanup configuration."""

    autoclean_interval_s: int = Field(default=2592000, ge=3600)  # At least 1 hour
    n_history_slots: int = Field(default=10, ge=1, le=50)


class ThemeColorsConfig(BaseModel):
    """Theme color configuration."""

    table_bg_main: str
    table_bg_2: str
    table_bg_header: str
    table_fg_main: str
    table_fg_header: str
    table_sep: str


class ThemeConfig(BaseModel):
    """Theme configuration - loaded from theme files."""

    table_theme: str
    main: ThemeColorsConfig
    row_mark: str
    alt: dict[str, str]
    columns: dict[str, str]
    records: dict[str, str]
    cell_values: dict[str, str]
    marks: dict[str, str]
    rating_scale: list[str]
    alt_rating_scale: list[str]
    figures: dict[str, Any]
    color_palette_positions: list[str]
    footer: dict[str, str]
    topbar: dict[str, str]
    balance: dict[str, str]
    notepaper: dict[str, str]
    notebook: dict[str, str]
    noteeditor_dialog: dict[str, str]

    @field_validator("rating_scale", "alt_rating_scale")
    @classmethod
    def validate_rating_scales(cls, v):
        if len(v) != 9:
            raise ValueError("Rating scales must have exactly 9 colors")
        return v

    @field_validator("color_palette_positions")
    @classmethod
    def validate_color_palette(cls, v):
        if len(v) < 10:
            raise ValueError("Color palette must have at least 10 colors")
        return v


class Config(BaseModel):
    """Complete SRTJ configuration."""

    app: AppConfig = Field(default_factory=AppConfig)
    startup: StartupConfig = Field(default_factory=StartupConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    scope: ScopeConfig = Field(default_factory=ScopeConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    balance: BalanceConfig = Field(default_factory=BalanceConfig)
    statistics: StatisticsConfig = Field(default_factory=StatisticsConfig)
    notes: NotesConfig = Field(default_factory=NotesConfig)
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    maintenance: MaintenanceConfig = Field(default_factory=MaintenanceConfig)
    themes: ThemeConfig

    model_config = {"extra": "forbid", "validate_assignment": True}
