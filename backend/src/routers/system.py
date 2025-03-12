from fastapi import APIRouter
from src.core.config import settings
import time

router = APIRouter(tags=["system"])

@router.get("/v1/api/ping")
async def get_ping():
    return {
        "uptime": int(time.time()-settings.SERVER_START_TIME)
    }

