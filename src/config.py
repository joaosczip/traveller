from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    EXCHANGE_RATE_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"
    CURRENCY_CACHE_KEY: str = "currency_rates"
    CURRENCY_CACHE_EXPIRE_SECONDS: int = 3600

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
