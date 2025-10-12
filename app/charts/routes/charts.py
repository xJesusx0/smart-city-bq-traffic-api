from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional

from app.core.database.mongo.mongo import mongodb
from app.charts.models.charts import TimeLineResponse, DatasetResponse

charts_router = APIRouter(prefix="/api/charts", tags=["Charts"])


@charts_router.get("/vehicle-timeline")
async def get_vehicle_timeline(
    location_id: Optional[int] = None,
    hours: int = Query(
        24, ge=1, le=168, description="Horas hacia atrás (máx 1 semana)"
    ),
):
    """
    Datos para gráfica de línea: Vehículos detectados en el tiempo

    Returns:
        {
            "labels": ["10:00", "11:00", "12:00", ...],
            "datasets": [{
                "label": "Vehículos detectados",
                "data": [15, 23, 18, ...]
            }]
        }
    """
    try:
        collection = mongodb.db["traffic_metrics"]
        start_date = datetime.now() - timedelta(hours=hours)

        # Construir query
        match_query = {"timestamp": {"$gte": start_date}}
        if location_id:
            match_query["location_id"] = location_id

        # Pipeline de agregación
        pipeline = [
            {"$match": match_query},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$timestamp"},
                        "month": {"$month": "$timestamp"},
                        "day": {"$dayOfMonth": "$timestamp"},
                        "hour": {"$hour": "$timestamp"},
                    },
                    "avg_vehicles": {"$avg": "$vehicle_count"},
                    "total_vehicles": {"$sum": "$vehicle_count"},
                    "sample_count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        results = await collection.aggregate(pipeline).to_list(length=hours)

        # Formatear para Chart.js
        labels = []
        data = []

        for item in results:
            date_parts = item["_id"]
            # Formato: "10/11 14:00"
            label = f"{date_parts['day']:02d}/{date_parts['month']:02d} {date_parts['hour']:02d}:00"
            labels.append(label)
            data.append(round(item["avg_vehicles"], 1))

        time_line_response = TimeLineResponse(
            labels=labels,
            data=[
                DatasetResponse(
                    label="Vehículos detectados",
                    data=data,
                    border_color="rgb(75, 192, 192)",
                    background_color="rgba(75, 192, 192, 0.2)",
                    tension=0.4,
                )
            ],
        )
        return time_line_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@charts_router.get("/location-comparison")
async def get_location_comparison(hours: int = Query(24, ge=1, le=168)):
    """
    Datos para gráfica de barras: Comparación de ubicaciones

    Returns:
        {
            "labels": ["Calle 72", "Av. Boyacá", ...],
            "datasets": [{
                "label": "Promedio de vehículos",
                "data": [45, 67, 32, ...]
            }]
        }
    """
    try:
        collection = mongodb.db["traffic_metrics"]
        start_date = datetime.now() - timedelta(hours=hours)

        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": "$location_id",
                    "avg_vehicles": {"$avg": "$vehicle_count"},
                    "total_samples": {"$sum": 1},
                }
            },
            {"$sort": {"avg_vehicles": -1}},
        ]

        results = await collection.aggregate(pipeline).to_list(length=100)

        # Formatear para Chart.js
        labels = [f"Ubicación {item['_id']}" for item in results]
        data = [round(item["avg_vehicles"], 1) for item in results]

        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Promedio de vehículos",
                    "data": data,
                    "backgroundColor": [
                        "rgba(255, 99, 132, 0.5)",
                        "rgba(54, 162, 235, 0.5)",
                        "rgba(255, 206, 86, 0.5)",
                        "rgba(75, 192, 192, 0.5)",
                        "rgba(153, 102, 255, 0.5)",
                    ],
                }
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@charts_router.get("/vehicle-types")
async def get_vehicle_type_distribution(
    location_id: Optional[int] = None, hours: int = Query(24, ge=1, le=168)
):
    """
    Datos para gráfica de pie/dona: Distribución de tipos de vehículos

    Returns:
        {
            "labels": ["Carros", "Motos", "Buses", "Peatones"],
            "datasets": [{
                "data": [156, 45, 12, 23]
            }]
        }
    """
    try:
        collection = mongodb.db["traffic_metrics"]
        start_date = datetime.now() - timedelta(hours=hours)

        # Construir query
        match_query = {"timestamp": {"$gte": start_date}}
        if location_id:
            match_query["location_id"] = location_id

        # Pipeline para contar por tipo
        pipeline = [
            {"$match": match_query},
            {"$unwind": "$detections"},
            {"$group": {"_id": "$detections.class_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]

        results = await collection.aggregate(pipeline).to_list(length=20)

        # Mapear nombres en español
        name_mapping = {
            "car": "Carros",
            "motorcycle": "Motos",
            "bus": "Buses",
            "truck": "Camiones",
            "person": "Peatones",
            "bicycle": "Bicicletas",
        }

        labels = [name_mapping.get(item["_id"], item["_id"]) for item in results]
        data = [item["count"] for item in results]

        return {
            "labels": labels,
            "datasets": [
                {
                    "data": data,
                    "backgroundColor": [
                        "rgba(255, 99, 132, 0.8)",
                        "rgba(54, 162, 235, 0.8)",
                        "rgba(255, 206, 86, 0.8)",
                        "rgba(75, 192, 192, 0.8)",
                        "rgba(153, 102, 255, 0.8)",
                        "rgba(255, 159, 64, 0.8)",
                    ],
                }
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@charts_router.get("/hourly-heatmap")
async def get_hourly_heatmap(location_id: int, days: int = Query(7, ge=1, le=30)):
    """
    Datos para heatmap: Intensidad de tráfico por hora del día

    Returns:
        {
            "hours": [0, 1, 2, ..., 23],
            "data": [
                [12, 15, 18, ...],  # Lunes
                [10, 14, 20, ...],  # Martes
                ...
            ],
            "days": ["Lun", "Mar", "Mié", ...]
        }
    """
    try:
        collection = mongodb.db["traffic_metrics"]
        start_date = datetime.now() - timedelta(days=days)

        pipeline = [
            {"$match": {"location_id": location_id, "timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "dayOfWeek": {"$dayOfWeek": "$timestamp"},
                        "hour": {"$hour": "$timestamp"},
                    },
                    "avg_vehicles": {"$avg": "$vehicle_count"},
                }
            },
            {"$sort": {"_id.dayOfWeek": 1, "_id.hour": 1}},
        ]

        results = await collection.aggregate(pipeline).to_list(length=200)

        # Organizar en matriz [día][hora]
        day_names = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
        hours = list(range(24))

        # Inicializar matriz
        data_matrix = [[0 for _ in range(24)] for _ in range(7)]

        for item in results:
            day = item["_id"]["dayOfWeek"] - 1  # MongoDB: 1=Domingo
            hour = item["_id"]["hour"]
            data_matrix[day][hour] = round(item["avg_vehicles"], 1)

        return {"hours": hours, "days": day_names, "data": data_matrix}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@charts_router.get("/summary")
async def get_dashboard_summary(location_id: Optional[int] = None):
    """
    Resumen para dashboard: KPIs principales

    Returns:
        {
            "total_samples": 1234,
            "avg_vehicles_today": 45.3,
            "peak_hour": "18:00",
            "most_common_vehicle": "car"
        }
    """
    try:
        collection = mongodb.db["traffic_metrics"]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        match_query = {"timestamp": {"$gte": today}}
        if location_id:
            match_query["location_id"] = location_id

        # Total de muestras
        total_samples = await collection.count_documents(match_query)

        # Promedio de vehículos hoy
        pipeline_avg = [
            {"$match": match_query},
            {"$group": {"_id": None, "avg_vehicles": {"$avg": "$vehicle_count"}}},
        ]
        avg_result = await collection.aggregate(pipeline_avg).to_list(length=1)
        avg_vehicles = round(avg_result[0]["avg_vehicles"], 1) if avg_result else 0

        # Hora pico
        pipeline_peak = [
            {"$match": match_query},
            {
                "$group": {
                    "_id": {"$hour": "$timestamp"},
                    "avg_vehicles": {"$avg": "$vehicle_count"},
                }
            },
            {"$sort": {"avg_vehicles": -1}},
            {"$limit": 1},
        ]
        peak_result = await collection.aggregate(pipeline_peak).to_list(length=1)
        peak_hour = f"{peak_result[0]['_id']:02d}:00" if peak_result else "N/A"

        # Tipo de vehículo más común
        pipeline_common = [
            {"$match": match_query},
            {"$unwind": "$detections"},
            {"$group": {"_id": "$detections.class_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1},
        ]
        common_result = await collection.aggregate(pipeline_common).to_list(length=1)
        most_common = common_result[0]["_id"] if common_result else "N/A"

        return {
            "total_samples": total_samples,
            "avg_vehicles_today": avg_vehicles,
            "peak_hour": peak_hour,
            "most_common_vehicle": most_common,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
