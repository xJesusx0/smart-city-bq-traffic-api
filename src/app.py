from app.core.settings import settings


def run() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.env == "development",
        log_level="debug" if settings.env == "development" else "info",
    )


if __name__ == "__main__":
    run()
