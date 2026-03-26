from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

health_router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Respuesta del health check"""

    status: str
    service: str
    mysql_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.now)


@health_router.get("/", response_model=HealthResponse)
async def health_check():
    """Endpoint para verificar el estado del servicio"""
    return HealthResponse(
        status="ok",
        service="Video Analysis Service",
        mysql_loaded=True,
    )
