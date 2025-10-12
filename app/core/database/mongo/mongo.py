from app.core.models.analysis_response import AnalysisResponse
from app.core.settings import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime


class MongoDB:
    """Cliente de MongoDB para almacenar métricas de tráfico"""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        """Conectar a MongoDB"""
        try:
            print(f"🔌 Conectando a MongoDB: {settings.mongodb_url}")
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            self.db = self.client[settings.mongodb_database]

            # Verificar conexión
            await self.client.admin.command("ping")
            print(
                f"✅ Conectado a MongoDB - Base de datos: {settings.mongodb_database}"
            )

            # Crear índices
            await self._create_indexes()

        except Exception as e:
            print(f"❌ Error al conectar a MongoDB: {e}")
            raise

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


# Instancia global
mongodb = MongoDB()
