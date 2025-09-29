from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes.auth import auth_router
from app.core.settings import settings

router = APIRouter(prefix="/api")

app = FastAPI()


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
