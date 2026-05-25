from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str | None = Field(None, env="DATABASE_URL")
    db_host: str = Field("127.0.0.1", env="DB_HOST")
    db_port: int = Field(5432, env="DB_PORT")
    db_user: str = Field("postgres", env="DB_USER")
    db_password: str = Field("", env="DB_PASSWORD")
    db_name: str = Field("postgres", env="DB_NAME")
    db_allow_sqlite_fallback: bool = Field(True, env="DB_ALLOW_SQLITE_FALLBACK")
    secret_key: str = Field(
        "b2c8a9f6d4e51234abcd5678ef901234567890abcdef1234567890abcdef1234",
        env="SECRET_KEY",
    )

    class Config:
        env_file = ".env"


settings = Settings()
