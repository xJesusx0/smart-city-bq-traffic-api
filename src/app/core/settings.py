import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_host: str = os.getenv("APP_HOST")
    app_port: int = os.getenv("APP_PORT")
    env: str = os.getenv("ENV")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_expiration_time: int = int(os.getenv("JWT_EXPIRATION_TIME_MINUTES", 30))

load_dotenv()
settings = Settings()
