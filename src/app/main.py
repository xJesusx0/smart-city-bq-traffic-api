from fastapi import FastAPI, APIRouter

from src.app.auth.routes.auth import auth_router

router = APIRouter(prefix="/api")

app = FastAPI()

app.include_router(router)
app.include_router(auth_router)


@router.get("/")
async def root():
    return {"mensaje": "Hola mundo"}
