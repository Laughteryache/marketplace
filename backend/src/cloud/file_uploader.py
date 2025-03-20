from fastapi import HTTPException
from .super_secret import SERVICE_ACCOUNT_INFO
import asyncio
import json
import os
import httpx
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from loguru import logger



SCOPES = ["https://www.googleapis.com/auth/drive"]
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
PERMISSION_URL = "https://www.googleapis.com/drive/v3/files/{}/permissions"
UPLOAD_DIR = "src/uploaded_files"

async def random_file_name() -> str:
    return ''.join(random.choices(string.ascii_letters, k=50))



@logger.catch
async def get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(SERVICE_ACCOUNT_INFO), scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials.token


@logger.catch
async def upload_file(file_name, folder_id=None):
    file_path = os.path.join(UPLOAD_DIR, file_name)
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
    return file_id


@logger.catch
async def make_file_public(file_id):
    """Делает файл доступным по публичной ссылке"""
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    permission_data = {"role": "reader", "type": "anyone"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            PERMISSION_URL.format(file_id), headers=headers, json=permission_data
        )
        response.raise_for_status()
    logger.debug(f'Avatar made public: {file_id}')
    return file_id


@logger.catch
async def delete_file(file_name):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    try:
        loop = asyncio.get_event_loop()
        if os.path.exists(file_path):
            await loop.run_in_executor(None, os.remove, file_path)
            logger.info(f"Файл {file_name} успешно удалён из {UPLOAD_DIR}")
        else:
            logger.warning(f"Файл {file_name} не найден в {UPLOAD_DIR}")
    except Exception as e:
        logger.error(f"Ошибка при удалении файла {file_name}: {e}")


@logger.catch
async def get_new_avatar_id(file_name):
    try:
        file_id = await upload_file(file_name)
        link = await make_file_public(file_id)
        return link
    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_name}: {e}")
        raise HTTPException(status_code=500, detail=e)
    finally:
        await delete_file(file_name)

