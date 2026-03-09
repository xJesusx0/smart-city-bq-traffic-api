import json
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_geo_info_service, validate_token
from app.geo.models.geo_info_service_models import Intersection
from app.main import app

client = TestClient(app)


# Helper for mock token payload
def get_mock_payload():
    return {"sub": "test@example.com"}


# Override the dependency globally for the test session if needed,
# or use a fixture.
@pytest.fixture
def authenticated_client():
    app.dependency_overrides[validate_token] = get_mock_payload
    yield client
    app.dependency_overrides.clear()


def test_heartbeat_success():
    with patch("app.traffic.routes.intersection.get_redis_client") as mock_get_redis:
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        payload = {
            "device_name": "esp32-semaforo-1",
            "ip": "192.168.1.123",
            "semaforo1_verde": 20,
            "semaforo2_verde": 20,
            "all_red_time": 2,
            "estado_restante_s": 1,
            "ciclo_restante_s": 41,
            "next_semaforo1": 20,
            "next_semaforo2": 20,
            "next_fetched": False,
            "estado": "S1_ROJO_AMARILLO",
        }

        response = client.post("/api/intersections/1/heartbeat", json=payload)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_get_all_intersections_success(authenticated_client):
    with patch("app.traffic.routes.intersection.get_redis_client") as mock_get_redis:
        # Mock GeoInfoService
        mock_geo_service = MagicMock()
        app.dependency_overrides[get_geo_info_service] = lambda: mock_geo_service

        # Mock intersections from GeoInfoService
        mock_geo_service.get_intersections.return_value = [
            Intersection(id=1, street_a_name="Calle 1", street_b_name="Calle 2"),
            Intersection(id=2, street_a_name="Calle 3", street_b_name="Calle 4"),
        ]

        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        # Mock redis keys and get
        mock_redis.keys.return_value = ["intersection:1:state"]

        mock_data_1 = {
            "intersection_id": 1,
            "device_name": "esp32-1",
            "ip": "1.1.1.1",
            "semaforo1_verde": 20,
            "semaforo2_verde": 20,
            "all_red_time": 2,
            "estado_restante_s": 1,
            "ciclo_restante_s": 41,
            "next_semaforo1": 20,
            "next_semaforo2": 20,
            "next_fetched": False,
            "estado": "S1_VERDE",
            "last_seen": int(time.time()),
        }

        mock_redis.get.return_value = json.dumps(mock_data_1)

        response = authenticated_client.get(
            "/api/intersections", headers={"Authorization": "Bearer mock-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Intersection 1 should have realtime_data
        assert data[0]["id"] == 1
        assert data[0]["realtime_data"]["device_name"] == "esp32-1"

        # Intersection 2 should NOT have realtime_data
        assert data[1]["id"] == 2
        assert data[1]["realtime_data"] is None


def test_get_all_intersections_unauthorized():
    app.dependency_overrides.clear()
    response = client.get("/api/intersections")
    assert response.status_code == 401
