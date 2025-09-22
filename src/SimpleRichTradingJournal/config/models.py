from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from typing import List, Literal, Optional
from pathlib import Path

class Theme(BaseModel):
    table: dict[str, str | None] = {}
    row: dict[str, str] = {}
    cell: dict[str, Optional[str]] = {}
    footer: dict[str, str] = {}
    balance: dict[str, str] = {}
    notepaper: dict[str, str] = {}

class App(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8050
    debug: bool = False
    quiet: bool = False

class UI(BaseModel):
    themes: Theme = Field(default_factory=Theme)
    log: dict[str, List[int]] = {}
    note: dict[str, bool | str] = {}
    balance: dict[str, bool] = {}
    statistics: dict[str, int | bool | str] = {}
    pagination: dict[str, int] = {}

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

    model_config = {"env_file": ".env", "extra": "ignore"}

    @validator("storage")
    def validate_backend(cls, v):
        if v.backend != "sqlalchemy":
            raise ValueError("Only SQLAlchemy backend supported")
        return v

    @validator("ui")
    def validate_log_orders(cls, v):
        asset_order: List[int] = v.log.get("col_order_asset", [])
        if len(asset_order) != 9:
            raise ValueError("col_order_asset must have 9 elements")
        return v