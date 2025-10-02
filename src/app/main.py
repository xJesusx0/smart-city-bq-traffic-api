from app.iam.routes.user import user_router
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes.auth import auth_router
from app.core.settings import settings

import logging

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
