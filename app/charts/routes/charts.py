from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.charts.models.charts import (
    BarDatasetResponse,
    DashboardSummaryResponse,
    DatasetResponse,
    HourlyHeatmapResponse,
    LocationComparisonResponse,
    PieDatasetResponse,
    TimeLineResponse,
    VehicleTypesResponse,
)
from app.core.dependencies import MongoDBDep

charts_router = APIRouter(prefix="/api/charts", tags=["Charts"])


@charts_router.get("/vehicle-timeline", response_model=TimeLineResponse)
async def get_vehicle_timeline(
    mongodb: MongoDBDep,
    location_id: Optional[int] = None,
    hours: int = Query(
        24, ge=1, le=168, description="Horas hacia atrás (máx 1 semana)"
    ),
):
    """
    Datos para gráfica de línea: Vehículos detectados en el tiempo
    """
    try:
        data = await mongodb.get_vehicle_timeline_data(location_id, hours)
        return TimeLineResponse(
            labels=data["labels"],
            data=[
                DatasetResponse(
                    label="Vehículos detectados",
                    data=data["data"],
                    border_color="rgb(75, 192, 192)",
                    background_color="rgba(75, 192, 192, 0.2)",
                    tension=0.4,
                )
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@charts_router.get("/location-comparison", response_model=LocationComparisonResponse)
async def get_location_comparison(
    mongodb: MongoDBDep, hours: int = Query(24, ge=1, le=168)
):
    """
    Datos para gráfica de barras: Comparación de ubicaciones
    """
    try:
        data = await mongodb.get_location_comparison_data(hours)
        return LocationComparisonResponse(
            labels=data["labels"],
            data=[
                BarDatasetResponse(
                    label="Promedio de vehículos",
                    data=data["data"],
                    background_color=[
                        "rgba(255, 99, 132, 0.5)",
                        "rgba(54, 162, 235, 0.5)",
                        "rgba(255, 206, 86, 0.5)",
                        "rgba(75, 192, 192, 0.5)",
                        "rgba(153, 102, 255, 0.5)",
                    ],
                )
            ],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@charts_router.get("/vehicle-types", response_model=VehicleTypesResponse)
async def get_vehicle_type_distribution(
    mongodb: MongoDBDep,
    location_id: Optional[int] = None,
    hours: int = Query(24, ge=1, le=168),
):
    """
    Datos para gráfica de pie/dona: Distribución de tipos de vehículos
    """
    try:
        data = await mongodb.get_vehicle_types_data(location_id, hours)
        return VehicleTypesResponse(
            labels=data["labels"],
            data=[
                PieDatasetResponse(
                    data=data["data"],
                    background_color=[
                        "rgba(255, 99, 132, 0.8)",
                        "rgba(54, 162, 235, 0.8)",
                        "rgba(255, 206, 86, 0.8)",
                        "rgba(75, 192, 192, 0.8)",
                        "rgba(153, 102, 255, 0.8)",
                        "rgba(255, 159, 64, 0.8)",
                    ],
                )
            ],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@charts_router.get("/hourly-heatmap", response_model=HourlyHeatmapResponse)
async def get_hourly_heatmap(
    mongodb: MongoDBDep, location_id: int, days: int = Query(7, ge=1, le=30)
):
    """
    Datos para heatmap: Intensidad de tráfico por hora del día
    """
    try:
        data = await mongodb.get_hourly_heatmap_data(location_id, days)

        return HourlyHeatmapResponse(
            hours=data["hours"], days=data["days"], data=data["data"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@charts_router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(mongodb: MongoDBDep, location_id: Optional[int] = None):
    """
    Resumen para dashboard: KPIs principales
    """
    try:
        data = await mongodb.get_dashboard_summary_data(location_id)

        return DashboardSummaryResponse(
            total_samples=data["total_samples"],
            avg_vehicles_today=data["avg_vehicles_today"],
            peak_hour=data["peak_hour"],
            most_common_vehicle=data["most_common_vehicle"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
