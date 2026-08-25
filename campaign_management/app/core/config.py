from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymsql://daolt:12345678@127.0.0.1:3306/campaign_db"
    SECRET_KEY: str = "8f3a9b2c1d4e5f60718293a4b5c6d7e8f901234567890abcdef1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_NAME: str = "Campaign Management API"
    DEBUG: bool = True

    class Config:
        env_file = ".env.example"


def get_settings() -> Settings:
    return Settings()