from app.core.models.analysis_response import AnalysisResponse
from app.core.settings import settings
from app.core.exceptions import get_internal_server_error_exception
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime, timedelta

import asyncio


class MongoDB:
    """Cliente de MongoDB para almacenar métricas de tráfico"""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    _connection_lock: Optional[asyncio.Lock] = None
    _is_connected: bool = False

    def __init__(self):
        self._connection_lock = asyncio.Lock()

    async def ensure_connection(self):
        """
        Asegurar que la conexión esté establecida
        Esta función se llama en cada operación para garantizar conexión en Vercel
        """
        if self._is_connected and self.client is not None and self.db is not None:
            return
        self._connection_lock = self._get_lock()
        async with self._connection_lock:
            # Double-check después de adquirir el lock
            if self._is_connected and self.client is not None and self.db is not None:
                return

            await self._connect()

    def _get_lock(self) -> asyncio.Lock:
        """Obtener o crear el lock de forma lazy"""
        if self._connection_lock is None:
            self._connection_lock = asyncio.Lock()
        return self._connection_lock

    async def _connect(self):
        try:
            print(f"🔌 Conectando a MongoDB: {settings.mongodb_url[:30]}...")
            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=10,  # Límite de conexiones para serverless
                retryWrites=True,
            )

            self.db = self.client[settings.mongodb_database]
            await self.client.admin.command("ping")

            self._is_connected = True
            print(
                f"✅ Conectado a MongoDB - Base de datos: {settings.mongodb_database}"
            )

            # Crear índices (solo si no existen)
            await self._create_indexes()
        except Exception as e:
            print(f"❌ Error al conectar a MongoDB: {e}")
            self._is_connected = False
            # No raise - permitir que la app continue y reintente en la próxima petición
            raise

    async def connect(self):
        await self.ensure_connection()

    async def _create_indexes(self):
        """Crear índices para optimizar consultas"""
        collection = self.db[settings.mongodb_collection]  # pyright: ignore[reportOptionalSubscript]

        # Índice compuesto por location_id y timestamp (consultas frecuentes)
        await collection.create_index(
            [("location_id", 1), ("timestamp", -1)], name="idx_location_timestamp"
        )

        # Índice por timestamp solo (consultas de rango de fechas)
        await collection.create_index([("timestamp", -1)], name="idx_timestamp")

        # Índice por location_id solo (filtros por ubicación)
        await collection.create_index([("location_id", 1)], name="idx_location_id")

        # Índice por vehicle_count (para queries de tráfico alto/bajo)
        await collection.create_index([("vehicle_count", -1)], name="idx_vehicle_count")

        # Índice geoespacial (para coordenadas latitude/longitude)
        # Ahora con formato GeoJSON correcto
        await collection.create_index(
            [("location", "2dsphere")], name="idx_location_geo"
        )

        print("📊 Índices de MongoDB creados")
        print("   - idx_location_timestamp (location_id + timestamp)")
        print("   - idx_timestamp (timestamp)")
        print("   - idx_location_id (location_id)")
        print("   - idx_vehicle_count (vehicle_count)")
        print("   - idx_coordinates (latitude + longitude)")
        print("   - idx_location_geo (GeoJSON para queries geoespaciales)")

    async def close(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()
            print("🔌 Conexión a MongoDB cerrada")

    async def get_metrics(
        self, location_id: Optional[int] = None, limit: int = 100, skip: int = 0
    ) -> list:
        """
        Obtener métricas de tráfico

        Args:
            location_id: Filtrar por ubicación (opcional)
            limit: Cantidad máxima de resultados
            skip: Cantidad de resultados a saltar (paginación)

        Returns:
            Lista de métricas
        """
        await self.ensure_connection()
        if self.db is None:
            raise get_internal_server_error_exception(
                "No hay conexión a la base de datos de metricas"
            )

        collection = self.db[settings.mongodb_collection]

        # Construir filtro
        query = {}
        if location_id:
            query["location_id"] = location_id

        # Ejecutar consulta
        cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        metrics = await cursor.to_list(length=limit)

        # Convertir ObjectId a string
        for metric in metrics:
            metric["_id"] = str(metric["_id"])

        return metrics

    async def get_metric_by_id(self, metric_id: str) -> Optional[dict]:
        """Obtener una métrica específica por ID"""
        from bson import ObjectId

        await self.ensure_connection()

        if self.db is None:
            raise get_internal_server_error_exception(
                "No hay conexión a la base de datos de metricas"
            )

        collection = self.db[settings.mongodb_collection]

        try:
            metric = await collection.find_one({"_id": ObjectId(metric_id)})
            if metric:
                metric["_id"] = str(metric["_id"])
            return metric
        except Exception as e:
            print(f"❌ Error al buscar métrica: {e}")
            return None

    async def get_stats_by_location(self, location_id: int) -> dict:
        """
        Obtener estadísticas agregadas por ubicación

        Returns:
            Diccionario con estadísticas
        """
        if self.db is None:
            raise get_internal_server_error_exception(
                "No hay conexión a la base de datos de metricas"
            )
        collection = self.db[settings.mongodb_collection]

        pipeline = [
            {"$match": {"location_id": location_id}},
            {
                "$group": {
                    "_id": "$location_id",
                    "total_samples": {"$sum": 1},
                    "avg_vehicles": {"$avg": "$vehicle_count"},
                    "max_vehicles": {"$max": "$vehicle_count"},
                    "min_vehicles": {"$min": "$vehicle_count"},
                    "avg_processing_time": {"$avg": "$processing_time"},
                }
            },
        ]

        result = await collection.aggregate(pipeline).to_list(length=1)

        if result:
            return result[0]
        return {}

    async def get_hourly_stats(self, location_id: int, hours: int = 24) -> list:
        """
        Obtener estadísticas por hora

        Args:
            location_id: ID de la ubicación
            hours: Cantidad de horas hacia atrás

        Returns:
            Lista de estadísticas por hora
        """
        from datetime import timedelta

        if self.db is None:
            raise get_internal_server_error_exception(
                "No hay conexión a la base de datos de metricas"
            )
        collection = self.db[settings.mongodb_collection]

        start_date = datetime.now() - timedelta(hours=hours)

        pipeline = [
            {"$match": {"location_id": location_id, "timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$timestamp"},
                        "month": {"$month": "$timestamp"},
                        "day": {"$dayOfMonth": "$timestamp"},
                        "hour": {"$hour": "$timestamp"},
                    },
                    "avg_vehicles": {"$avg": "$vehicle_count"},
                    "max_vehicles": {"$max": "$vehicle_count"},
                    "sample_count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": -1}},
        ]

        return await collection.aggregate(pipeline).to_list(length=hours)

    async def get_nearby_metrics(
        self,
        latitude: float,
        longitude: float,
        max_distance_km: float = 5.0,
        limit: int = 10,
    ) -> list:
        """
        Obtener métricas de cámaras cercanas a una ubicación

        Args:
            latitude: Latitud de la ubicación de referencia
            longitude: Longitud de la ubicación de referencia
            max_distance_km: Radio de búsqueda en kilómetros
            limit: Cantidad máxima de resultados

        Returns:
            Lista de métricas ordenadas por proximidad

        Ejemplo:
            # Buscar cámaras a menos de 5km de una ubicación
            nearby = await mongodb.get_nearby_metrics(
                latitude=10.9878,
                longitude=-74.7889,
                max_distance_km=5.0
            )
        """
        if self.db is None:
            raise get_internal_server_error_exception(
                "No hay conexión a la base de datos de metricas"
            )

        collection = self.db[settings.mongodb_collection]

        # Query geoespacial $near
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude],  # [lon, lat]
                    },
                    "$maxDistance": max_distance_km * 1000,  # Convertir a metros
                }
            }
        }

        cursor = collection.find(query).limit(limit)
        metrics = await cursor.to_list(length=limit)

        # Convertir ObjectId a string
        for metric in metrics:
            metric["_id"] = str(metric["_id"])

        return metrics

    # Agregar estos métodos a tu clase MongoDB

    async def get_vehicle_timeline_data(
        self, location_id: Optional[int] = None, hours: int = 24
    ) -> dict:
        """
        Obtener datos para gráfica de timeline
        """
        await self.ensure_connection()

        if self.db is None:
            raise Exception("No hay conexión a la base de datos")

        collection = self.db[settings.mongodb_collection]
        start_date = datetime.now() - timedelta(hours=hours)

        # Construir query
        match_query: dict = {"timestamp": {"$gte": start_date}}
        if location_id:
            match_query["location_id"] = location_id

        # Pipeline
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

        # Formatear
        labels = []
        data = []

        for item in results:
            date_parts = item["_id"]
            label = f"{date_parts['day']:02d}/{date_parts['month']:02d} {date_parts['hour']:02d}:00"
            labels.append(label)
            data.append(round(item["avg_vehicles"], 1))

        return {"labels": labels, "data": data}

    async def get_location_comparison_data(self, hours: int = 24) -> dict:
        """
        Obtener datos para comparación de ubicaciones
        """
        await self.ensure_connection()

        if self.db is None:
            raise Exception("No hay conexión a la base de datos")

        collection = self.db[settings.mongodb_collection]
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

        labels = [f"Ubicación {item['_id']}" for item in results]
        data = [round(item["avg_vehicles"], 1) for item in results]

        return {"labels": labels, "data": data}

    async def get_vehicle_types_data(
        self, location_id: Optional[int] = None, hours: int = 24
    ) -> dict:
        """
        Obtener distribución de tipos de vehículos
        """
        await self.ensure_connection()

        if self.db is None:
            raise Exception("No hay conexión a la base de datos")

        collection = self.db[settings.mongodb_collection]
        start_date = datetime.now() - timedelta(hours=hours)

        match_query: dict = {"timestamp": {"$gte": start_date}}
        if location_id:
            match_query["location_id"] = location_id

        pipeline = [
            {"$match": match_query},
            {"$unwind": "$detections"},
            {"$group": {"_id": "$detections.class_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]

        results = await collection.aggregate(pipeline).to_list(length=20)

        # Mapear nombres
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

        return {"labels": labels, "data": data}

    async def get_hourly_heatmap_data(self, location_id: int, days: int = 7) -> dict:
        """
        Obtener datos para heatmap por hora
        """
        await self.ensure_connection()

        if self.db is None:
            raise Exception("No hay conexión a la base de datos")

        collection = self.db[settings.mongodb_collection]
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

        # Organizar matriz
        day_names = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
        hours_list = list(range(24))
        data_matrix = [[0.0 for _ in range(24)] for _ in range(7)]

        for item in results:
            day = item["_id"]["dayOfWeek"] - 1
            hour = item["_id"]["hour"]
            data_matrix[day][hour] = round(item["avg_vehicles"], 1)

        return {"hours": hours_list, "days": day_names, "data": data_matrix}

    async def get_dashboard_summary_data(
        self, location_id: Optional[int] = None
    ) -> dict:
        """
        Obtener resumen para dashboard
        """
        await self.ensure_connection()

        if self.db is None:
            raise Exception("No hay conexión a la base de datos")

        collection = self.db[settings.mongodb_collection]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        match_query: dict = {"timestamp": {"$gte": today}}
        if location_id:
            match_query["location_id"] = location_id

        # Total de muestras
        total_samples = await collection.count_documents(match_query)

        # Promedio de vehículos
        pipeline_avg = [
            {"$match": match_query},
            {"$group": {"_id": None, "avg_vehicles": {"$avg": "$vehicle_count"}}},
        ]
        avg_result = await collection.aggregate(pipeline_avg).to_list(length=1)
        avg_vehicles = round(avg_result[0]["avg_vehicles"], 1) if avg_result else 0.0

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

        # Tipo más común
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


# Instancia global
mongodb = MongoDB()
