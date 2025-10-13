
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int = 10080 # 7 days

    class Config:
        env_file = ".env"

settings = Settings()
