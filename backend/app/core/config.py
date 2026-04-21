from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration.

    All external-API credentials default to empty strings so the app boots
    cleanly with stub adapters. Providing values unlocks real integrations.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    env: str = Field(default="dev", validation_alias="WILLIEPB_ENV")
    log_level: str = Field(default="INFO", validation_alias="WILLIEPB_LOG_LEVEL")
    database_url: str = Field(
        default="sqlite:///./williepb.db", validation_alias="WILLIEPB_DATABASE_URL"
    )
    base_currency: str = Field(default="KRW", validation_alias="WILLIEPB_BASE_CURRENCY")

    upbit_access_key: str = Field(default="", validation_alias="UPBIT_ACCESS_KEY")
    upbit_secret_key: str = Field(default="", validation_alias="UPBIT_SECRET_KEY")
    ecos_api_key: str = Field(default="", validation_alias="ECOS_API_KEY")
    molit_api_key: str = Field(default="", validation_alias="MOLIT_API_KEY")
    reb_api_key: str = Field(default="", validation_alias="REB_API_KEY")
    kiwoom_app_key: str = Field(default="", validation_alias="KIWOOM_APP_KEY")
    kiwoom_app_secret: str = Field(default="", validation_alias="KIWOOM_APP_SECRET")
    nh_app_key: str = Field(default="", validation_alias="NH_APP_KEY")
    nh_app_secret: str = Field(default="", validation_alias="NH_APP_SECRET")

    jwt_secret: str = Field(default="", validation_alias="WILLIEPB_JWT_SECRET")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
