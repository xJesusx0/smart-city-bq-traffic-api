# src/app/core/settings.py

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Proporciona los valores por defecto directamente.
    app_host: str = "localhost"
    app_port: int = 8080
    env: str = "production"
    jwt_secret_key: str = "secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_time: int = 1  # tiempo en dias
    db_url: str = ""

    allowed_hosts: list[str] = []

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def build_allowed_hosts(cls, value: str | list[str]) -> str | list[str]:
        if isinstance(value, str) and value:
            return [host.strip() for host in value.split(",")]

        # Si el valor es una lista (o nulo/vacío), lo devuelve tal cual.
        if isinstance(value, list):
            return value
        return []  # Devuelve lista vacía si no hay nada


settings = Settings()
