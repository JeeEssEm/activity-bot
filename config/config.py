from pydantic_settings import BaseSettings


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

    class Config:
        env_file = '.env'


settings = Settings()


def get_database_url():
    if settings.DEBUG:
        return 'sqlite+aiosqlite:///./db.sqlite'
    return f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'
