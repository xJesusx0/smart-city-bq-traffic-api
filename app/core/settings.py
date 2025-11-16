# src/app/core/settings.py

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.email.models.email import EmailSettings

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

    mongodb_url: str = "mongodb://admin:admin123@localhost:27017"
    mongodb_database: str = "smart_traffic"
    mongodb_collection: str = "traffic_metrics"

    google_client_id: str = ""

    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_from_name: str = ""
    mail_server: str = ""
    template_folder: str = ""
    mail_port: int = 587
    change_password_url: str = ""

    geo_info_service_url: str = ""
    geo_info_service_api_key: str = ""

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
email_settings = EmailSettings(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    TEMPLATE_FOLDER=settings.template_folder,
)
