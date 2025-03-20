from fastapi import File, UploadFile, HTTPException

from .utils import random_file_name
import aiofiles

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # ограничение 5 MB


async def check_uploaded_file(
        file: UploadFile = File(...)
) -> str | HTTPException:
    filename = file.filename
    file_extension = filename[filename.rfind("."):].lower()  # Получаем расширение файла
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_extension!r}. Allowed formats are {ALLOWED_EXTENSIONS}")
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024} MB.")
    try:
        new_file_name = await random_file_name()
        new_file_path = f"src/uploaded_files/{new_file_name}{file_extension}"
        content = await file.read()
        async with aiofiles.open(new_file_path, "wb") as f:
            await f.write(content)
        return f'{new_file_name}{file_extension}'
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))