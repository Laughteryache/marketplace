import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.routers.system import router as system_router
from src.routers.auth import router as auth_router
from src.core.database.helper import db_helper
from loguru import logger
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import time

@logger.catch
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        yield
    finally:
        server_uptime = int(time.time() - settings.SERVER_START_TIME)
        shutdown_time = int(time.time())
        logger.info(f"Server total uptime: {server_uptime}")
        logger.info(f"Shutdown time: {shutdown_time}")
        await db_helper.dispose()
main_app = FastAPI(lifespan=lifespan)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app.include_router(system_router)
main_app.include_router(auth_router)


def start_server():

    uvicorn.run(
        app='main:main_app',
        host=settings.IP_ADDRESS,
        port=settings.SERVER_PORT,
        log_level="info",
        reload=True,
    )


if __name__ == "__main__":
    start_server()