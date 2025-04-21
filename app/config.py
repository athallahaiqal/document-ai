from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Models
    generation_model_name: str
    embeddings_model_name: str
    embeddings_dimensions: int

    # Database
    database_user: str
    database_password: str
    database_name: str
    database_host: str
    database_port: int

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
