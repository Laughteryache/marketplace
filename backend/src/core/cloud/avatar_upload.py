from super_secret import SERVICE_ACCOUNT_INFO
import asyncio
import json
import httpx
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from loguru import logger

SCOPES = ["https://www.googleapis.com/auth/drive"]
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
PERMISSION_URL = "https://www.googleapis.com/drive/v3/files/{}/permissions"


@logger.catch
async def get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(SERVICE_ACCOUNT_INFO), scopes=SCOPES
    )
    # Обновляем токен с помощью Request
    credentials.refresh(Request())
    return credentials.token


@logger.catch
async def upload_file(file_path, file_name, folder_id=None):
    """Асинхронно загружает файл в Google Drive"""
    token = await get_access_token()

    # Метаданные файла
    metadata = {"name": file_name}
    if folder_id:
        metadata["parents"] = [folder_id]

    # Открываем файл и готовим запрос
    with open(file_path, "rb") as file_data:
        files = {
            "metadata": ("metadata", json.dumps(metadata), "application/json"),
            "file": (file_name, file_data, "application/octet-stream"),
        }
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(UPLOAD_URL, headers=headers, files=files)
            response.raise_for_status()  # Проверяет HTTP статус
            response_data = response.json()

    file_id = response_data.get("id")
    print(f"Файл загружен! ID: {file_id}")
    return file_id


@logger.catch
async def make_file_public(file_id):
    """Делает файл доступным по ссылке"""
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    permission_data = {"role": "reader", "type": "anyone"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            PERMISSION_URL.format(file_id), headers=headers, json=permission_data
        )
        response.raise_for_status()  # Проверяет статус ответа
    logger.debug(f'{file_id} new avatar')
    return f"https://drive.google.com/file/d/{file_id}/preview"


@logger.catch
async def get_new_avatar_link(file_path, file_name):
    file_id = await upload_file(file_path, file_name)
    link = await make_file_public(file_id)
    return link
