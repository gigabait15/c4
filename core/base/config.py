from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    BOT_TOKEN: str
    API_BASE_URL: str = "http://localhost:8000"


settings = Settings()  # type: ignore[call-arg]
