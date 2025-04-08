from authx import AuthXConfig
from datetime import timedelta
import os

authx_config = AuthXConfig(
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY'),
        JWT_TOKEN_LOCATION=['cookies'],
        JWT_ACCESS_COOKIE_NAME='access_token',
        JWT_REFRESH_COOKIE_NAME='refresh_token',
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30))