from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'HalalVerify API'
    api_prefix: str = '/v1'
    database_url: str = Field(
        default=f"sqlite+aiosqlite:///{(Path(__file__).resolve().parents[1] / 'halalverify.db').as_posix()}"
    )
    seed_demo_data: bool = True
    developer_api_keys: str = 'demo-free-key,demo-trusted-key'
    free_rate_limit: str = '100/minute'
    api_key_rate_limit: str = '1000/minute'
    telegram_bot_token: str = ''
    halalverify_api_url: str = 'http://localhost:8000'
    request_timeout_seconds: float = 10.0

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @property
    def parsed_api_keys(self) -> set[str]:
        return {key.strip() for key in self.developer_api_keys.split(',') if key.strip()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
