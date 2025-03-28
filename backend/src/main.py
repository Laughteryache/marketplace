import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from global_config import settings

from auth.router import router as auth_router
from products.router import router as product_router
from profile.router import router as profile_router

from loguru import logger  # In the future, logging will occur on hosting instead of a log file # ElasticSearch in progress!
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import time


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application lifespan started")
    try:
        yield

    except Exception as e:
        logger.error(f"Error during application lifespan: {e}")

    finally:

        try:
            server_uptime = int(time.time() - settings.SERVER_START_TIME)
            logger.info(f"Server total uptime: {server_uptime} seconds")

        except Exception as dispose_error:
            logger.error(f"Error during cleanup: {dispose_error}")


main_app = FastAPI(lifespan=lifespan)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app.include_router(auth_router)
main_app.include_router(product_router)
main_app.include_router(profile_router)

@main_app.get("/ping")
async def get_ping():
    return {"uptime": int(time.time()-settings.SERVER_START_TIME)}



@logger.catch
def start_server():
    uvicorn.run(
        app='main:main_app',
        host=settings.IP_ADDRESS,
        port=settings.SERVER_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    start_server()

