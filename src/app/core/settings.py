import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_host: str = os.getenv("APP_HOST", "localhost")
    app_port: int = int(os.getenv("APP_PORT", "8080"))
    env: str = os.getenv("ENV", "production")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "secret")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_time: int = int(os.getenv("JWT_EXPIRATION_TIME_DAYS", 1))
    db_url: str = os.getenv("DB_URL", "")


load_dotenv()
settings = Settings()
