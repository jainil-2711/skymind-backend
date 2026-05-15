from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_ENV: str = "development"
    SECRET_KEY: str

    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Amadeus API
    AMADEUS_CLIENT_ID: str = "placeholder"
    AMADEUS_CLIENT_SECRET: str = "placeholder"
    AMADEUS_MOCK: str = "true"   # ← set to "false" when real keys are available

    # Claude API
    CLAUDE_API_KEY: str = "placeholder"

    # SendGrid
    SENDGRID_API_KEY: str = "placeholder"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()