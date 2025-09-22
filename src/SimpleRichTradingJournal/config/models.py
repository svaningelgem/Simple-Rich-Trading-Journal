from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from typing import List, Literal, Optional, Any
from pathlib import Path

class Theme(BaseModel):
    table: dict[str, str | None] = Field(default_factory=dict)
    row: dict[str, str] = Field(default_factory=dict)
    cell: dict[str, Optional[str]] = Field(default_factory=dict)
    footer: dict[str, str] = Field(default_factory=dict)
    balance: dict[str, str] = Field(default_factory=dict)
    notepaper: dict[str, str] = Field(default_factory=dict)
    rating_scale: List[str] = Field(default_factory=list)
    alt_rating_scale: List[str] = Field(default_factory=list)

class App(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8050
    debug: bool = False
    quiet: bool = False
    detach: bool = False
    administrative: bool = False

class UI(BaseModel):
    themes: Theme = Field(default_factory=Theme)
    log: dict[str, List[int]] = Field(default_factory=dict)
    col_order_asset: List[int] = Field(default_factory=list)
    col_order_note: List[int] = Field(default_factory=list)
    col_widths: List[int] = Field(default_factory=list)
    note: dict[str, bool | str] = Field(default_factory=dict)
    mathjax: bool = True
    cell_variable_formatter: bool = True
    file_drop_cloner: str = "own"
    balance: dict[str, bool] = Field(default_factory=dict)
    side_init_balance_value: bool = True
    t52w: bool = True
    current: bool = True
    years: bool = True
    quarters: bool = True
    statistics: dict[str, Any] = Field(default_factory=dict)
    sun_max_depth: int = 3
    group_default: List[bool] = Field(default_factory=list)
    performance: dict[str, Any] = Field(default_factory=dict)
    size_slider: int = 6
    steps: int = 12
    trailing_frame: str = "month"
    trailing_interval: int = 1
    range: str = "1y"
    hypothesis_per: bool = True
    pagination: dict[str, int] = {"per_page": 100}
    time_format_transaction: str = "%Y-%m-%d %H:%M:%S"
    time_format_history: str = "%Y-%m-%d %H:%M:%S"
    bottom_bar_distance_bottom: str = "10px"
    bottom_bar_distance_right: str = "10px"
    c1_width: str = "50%"
    grid_row3_height: int = 200

class Storage(BaseModel):
    backend: Literal["sqlalchemy"] = "sqlalchemy"
    url: str = "sqlite:///journal.db"
    plugin: Optional[str] = None

class Logging(BaseModel):
    rotation_mb: int = 500
    retention_days: int = 10

class Profiles(BaseModel):
    home_folder: str = "Trading-Journals.srtj"
    prefix: str = "%"
    demo_folder: str = "#demo"

class Config(BaseSettings):
    app: App
    ui: UI
    storage: Storage
    logging: Logging
    profiles: Profiles

    model_config = {"extra": "ignore"}

    @validator("ui")
    def validate_log_orders(cls, v):
        if len(v.col_order_asset) != 9:
            raise ValueError("col_order_asset must have 9 elements")
        if len(v.col_order_note) != 8:
            raise ValueError("col_order_note must have 8 elements")
        return v