import json
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import validate_token
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

        mock_redis.set.assert_called_once()
        args, kwargs = mock_redis.set.call_args
        key = args[0]
        value = json.loads(args[1])

        assert key == "intersection:1:state"
        assert value["intersection_id"] == 1
        assert "last_seen" in value
        assert kwargs["ex"] == 30


def test_get_all_intersections_success(authenticated_client):
    with patch("app.traffic.routes.intersection.get_redis_client") as mock_get_redis:
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        # Mock redis keys and get
        mock_redis.keys.return_value = ["intersection:1:state", "intersection:2:state"]

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
        mock_data_2 = {
            "intersection_id": 2,
            "device_name": "esp32-2",
            "ip": "1.1.1.2",
            "semaforo1_verde": 25,
            "semaforo2_verde": 25,
            "all_red_time": 2,
            "estado_restante_s": 5,
            "ciclo_restante_s": 50,
            "next_semaforo1": 25,
            "next_semaforo2": 25,
            "next_fetched": True,
            "estado": "S2_VERDE",
            "last_seen": int(time.time()),
        }

        mock_redis.get.side_effect = [json.dumps(mock_data_1), json.dumps(mock_data_2)]

        # Now headers are technically ignored by our override, but it's good practice
        response = authenticated_client.get(
            "/api/intersections", headers={"Authorization": "Bearer mock-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["intersection_id"] == 1
        assert data[1]["intersection_id"] == 2


def test_get_all_intersections_unauthorized():
    # Ensure no overrides for this test
    app.dependency_overrides.clear()
    response = client.get("/api/intersections")
    assert response.status_code == 401
