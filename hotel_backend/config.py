from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "root"
    db_name: str = "hotel_management"
    db_allow_sqlite_fallback: bool = True
    secret_key: str = "b2c8a9f6d4e51234abcd5678ef901234567890abcdef1234567890abcdef1234"

    class Config:
        env_file = ".env"

settings = Settings()
