from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "API Prode Mundial"
    VERSION: str = "1.0"
    DATABASE_URL: str = "sqlite:///./prode.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
