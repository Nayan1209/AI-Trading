from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: SecretStr | None = None
    groww_access_token: SecretStr | None = None
    groww_api_key: SecretStr | None = None
    groww_api_secret: SecretStr | None = None

settings = Settings()
