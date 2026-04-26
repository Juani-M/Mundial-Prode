from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "API Prode Mundial"
    VERSION: str = "1.0"
    DATABASE_URL: str = "sqlite:///./prode.db"

    SECRET_KEY: str = "tu_clave_super_secreta_aqui"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GOOGLE_CLIENT_ID: str = "279991018948-85nrnpicnd0unba94tpimrt10qleqirn.apps.googleusercontent.com"

    # API de deportes (football-data.org)
    SPORTS_API_KEY: str = ""
    SPORTS_API_BASE_URL: str = "https://api.football-data.org/v4"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

