import os

from pydantic_settings import BaseSettings, SettingsConfigDict


DOTENV = os.path.join(os.path.dirname(__file__), '.env')


class Settings(BaseSettings):
    DB_HOST: str = 'db host'
    DB_PORT: int = 5432
    DB_NAME: str = 'db name'
    DB_USER: str = 'db username'
    DB_PASSWORD: str = 'db pwd'

    DEBUG: bool = True
    INIT_MODELS: bool = True
    BOT_TOKEN: str = 'BOT_TOKEN'
    HSE_EMAIL: str = 'EMAIL'
    HSE_PASSWORD: str = 'PASSWORD'
    HSE_REFRESH_TOKEN: str | None = 'REFRESH_TOKEN'

    model_config = SettingsConfigDict(env_file=DOTENV)


settings = Settings()


def get_database_url(db_name=None):
    if not db_name:
        db_name = 'db'
    if settings.DEBUG:
        return f'sqlite+aiosqlite:///./{db_name}.sqlite'
    return f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'
