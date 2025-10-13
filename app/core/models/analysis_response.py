from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Coordenadas de la caja delimitadora"""

    x1: float = Field(..., description="Coordenada X superior izquierda")
    y1: float = Field(..., description="Coordenada Y superior izquierda")
    x2: float = Field(..., description="Coordenada X inferior derecha")
    y2: float = Field(..., description="Coordenada Y inferior derecha")


class VehicleDetection(BaseModel):
    """Detección individual de un vehículo"""

    class_name: str = Field(
        ..., description="Tipo de vehículo (car, bus, truck, motorcycle)"
    )
    confidence: float = Field(..., ge=0, le=1, description="Confianza de la detección")
    bbox: BoundingBox = Field(..., description="Coordenadas del vehículo")


class AnalysisRequest(BaseModel):
    """Request para análisis de imagen"""

    location_id: str = Field(default="default", description="ID de la ubicación/cámara")


class AnalysisResponse(BaseModel):
    """Respuesta del análisis de imagen"""

    success: bool = Field(..., description="Si el análisis fue exitoso")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Fecha/hora del análisis"
    )
    location_id: int = Field(..., description="ID de la ubicación")
    image_path: str = Field(..., description="Ruta donde se guardó la imagen")
    vehicle_count: int = Field(
        ..., ge=0, description="Cantidad total de vehículos detectados"
    )
    detections: list[VehicleDetection] = Field(
        default_factory=list, description="Lista de detecciones"
    )
    processing_time: float = Field(
        ..., description="Tiempo de procesamiento en segundos"
    )
    longitude: Optional[float] = Field(..., description="Longitud de la ubicación")
    latitude: Optional[float] = Field(..., description="Latitud de la ubicación")
    location_name: Optional[str] = Field(..., description="Nombre de la ubicación")


class HealthResponse(BaseModel):
    """Respuesta del health check"""

    status: str
    service: str
    model_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Respuesta de error"""

    success: bool = False
    error: str
    detail: Optional[str] = None
