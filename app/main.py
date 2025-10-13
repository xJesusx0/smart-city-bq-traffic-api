from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes.auth import auth_router
from app.core.settings import settings
from app.iam.routes.user import user_router
from app.iam.routes.role import role_router
from app.charts.routes.charts import charts_router

import logging
import uvicorn

router = APIRouter(prefix="/api")

app = FastAPI()

logging.basicConfig(level=logging.INFO)

app.add_middleware(
    # pyrefly: ignore
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(charts_router)


def start():
    """Función para iniciar el servidor"""
    uvicorn.run(
        "app.main:app", host=settings.app_host, port=settings.app_port, reload=True
    )


if __name__ == "__main__":
    start()
