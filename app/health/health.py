import logging
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.database.mongo.mongo import mongodb

health_router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Respuesta del health check"""

    status: str
    service: str
    mongodb_loaded: bool
    mysql_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.now)


@health_router.get("/", response_model=HealthResponse)
async def health_check():
    """Endpoint para verificar el estado del servicio"""
    return HealthResponse(
        status="ok",
        service="Video Analysis Service",
        mongodb_loaded=mongodb is not None,
        mysql_loaded=True,
    )


@health_router.get("/status/mongodb")
async def mongodb_status():
    """Endpoint para verificar el estado de la conexión a MongoDB"""
    try:
        logging.info("🔍 Verificando conexión a MongoDB...")
        await mongodb.client.admin.command("ping")
        return {"status": "MongoDB is connected"}
    except Exception as e:
        return {"status": "MongoDB is not connected", "error": str(e)}
