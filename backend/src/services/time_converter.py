import pytz
from datetime import datetime

async def convert_to_ekb_time(timestamp: datetime) -> datetime:
    ekb_timezone = pytz.timezone("Asia/Yekaterinburg")
    ekb_time = timestamp.astimezone(ekb_timezone)
    return ekb_time.date()
