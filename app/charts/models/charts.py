from pydantic import BaseModel


# ============================================
# Modelos Base para Datasets
# ============================================


class DatasetResponse(BaseModel):
    """Dataset para gráficas de línea"""

    label: str
    data: list[float]
    border_color: str
    background_color: str
    tension: float


class BarDatasetResponse(BaseModel):
    """Dataset para gráficas de barras"""

    label: str
    data: list[float]
    background_color: list[str]


class PieDatasetResponse(BaseModel):
    """Dataset para gráficas de pie/dona"""

    data: list[int]
    background_color: list[str]


# ============================================
# Respuestas para cada Endpoint
# ============================================


class TimeLineResponse(BaseModel):
    """Respuesta para gráfica de timeline"""

    labels: list[str]
    data: list[DatasetResponse]


class LocationComparisonResponse(BaseModel):
    """Respuesta para comparación de ubicaciones"""

    labels: list[str]
    data: list[BarDatasetResponse]


class VehicleTypesResponse(BaseModel):
    """Respuesta para distribución de tipos de vehículos"""

    labels: list[str]
    data: list[PieDatasetResponse]


class HourlyHeatmapResponse(BaseModel):
    """Respuesta para heatmap de tráfico por hora"""

    hours: list[int]
    days: list[str]
    data: list[list[float]]


class DashboardSummaryResponse(BaseModel):
    """Respuesta para resumen del dashboard"""

    total_samples: int
    avg_vehicles_today: float
    peak_hour: str
    most_common_vehicle: str
