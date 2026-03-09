import json
import time

from fastapi import APIRouter, Depends

from app.core.database.redis import get_redis_client
from app.core.dependencies import GeoInfoServiceDep, validate_token
from app.traffic.models.intersection import (
    HeartbeatResponse,
    IntersectionHeartbeat,
    IntersectionState,
    IntersectionWithStatus,
)

intersection_router = APIRouter(
    prefix="/api/geo/intersections", tags=["intersections", "geo"]
)


@intersection_router.post(
    "/{intersection_id}/heartbeat", response_model=HeartbeatResponse
)
async def heartbeat(intersection_id: int, data: IntersectionHeartbeat):
    key = f"intersection:{intersection_id}:state"

    # Calculate last_seen
    last_seen = int(time.time())

    # Create the state object to be stored in Redis
    state = data.model_dump()
    state["intersection_id"] = intersection_id
    state["last_seen"] = last_seen

    # Get redis client and save data with 30s TTL
    redis_client = get_redis_client()
    redis_client.set(key, json.dumps(state), ex=30)

    return HeartbeatResponse(status="ok")


@intersection_router.get(
    "",
    response_model=list[IntersectionWithStatus],
    dependencies=[Depends(validate_token)],
)
async def get_all_intersections(geo_service: GeoInfoServiceDep):
    # 1. Fetch registered intersections from GeoInfoService
    registered_intersections = await geo_service.get_intersections()
    # 2. Fetch all real-time states from Redis
    redis_client = get_redis_client()
    keys = redis_client.keys("intersection:*:state")

    realtime_states = {}
    for key in keys:
        data = redis_client.get(key)
        if data:
            state = IntersectionState(**json.loads(data))
            realtime_states[state.intersection_id] = state

    # 3. Merge data
    results = []
    for intersection in registered_intersections:
        # Create IntersectionWithStatus from Intersection data
        intersection_with_status = IntersectionWithStatus(**intersection.model_dump())

        # Link real-time data if available
        if intersection.id in realtime_states:
            intersection_with_status.realtime_data = realtime_states[intersection.id]

        results.append(intersection_with_status)

    return results
