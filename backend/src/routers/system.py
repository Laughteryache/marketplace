from fastapi import APIRouter
from core.config import settings
import time
from loguru import logger

router = APIRouter(tags=["system"])


@logger.catch
@router.get("/v1/api/ping")
async def get_ping():
    return {
        "uptime": int(time.time()-settings.SERVER_START_TIME)
    }

