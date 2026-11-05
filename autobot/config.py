from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "Autobot"
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    database_path: str = "./data/autobot.sqlite3"
    log_level: str = "INFO"
    ai_provider: str = "stub"
    ai_api_key: str = ""
    ai_model: str = ""
    obd_adapter: str = "simulator"
    obd_port: str = ""
    obd_poll_interval: float = 2.0
    obd_stale_after: float = 8.0
    obd_timeout: float = 2.0
    voice_input: str = "disabled"
    voice_output: str = "disabled"

    @property
    def database_file(self) -> Path:
        return Path(self.database_path)

@lru_cache
def get_settings() -> Settings:
    return Settings()
