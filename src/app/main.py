from fastapi import FastAPI, APIRouter

from src.app.auth.routes.auth import auth_router

app = FastAPI()

router = APIRouter(prefix="/api")

@router.get("/")
async def root():
    return {"mensaje": "Hola mundo"}

app.include_router(router)
app.include_router(auth_router)