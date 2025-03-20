import pytz
from datetime import datetime
import string
import random

async def convert_to_ekb_time(timestamp: datetime) -> datetime:
    ekb_timezone = pytz.timezone("Asia/Yekaterinburg")
    ekb_time = timestamp.astimezone(ekb_timezone)
    return ekb_time.date()


async def random_file_name() -> str:
    return ''.join(random.choices(string.ascii_letters, k=50))
