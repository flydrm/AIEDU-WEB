from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    ai_breaker_failures: int = 3
    ai_breaker_cooldown: int = 30
    cors_origins: str = "*"

    class Config:
        env_prefix = "APP_"
        case_sensitive = False

