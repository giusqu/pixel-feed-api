from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from src.security import get_current_user

router = APIRouter()

CHUNK_SIZE = 1024 * 1024
UPLOAD_DIR = Path("src/libs/images")


@router.post("/upload", status_code=201)
async def upload_file(file: UploadFile, current_user=Depends(get_current_user)):
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        file_path = UPLOAD_DIR / file.filename

        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file",
        )

    return {
        "detail": f"Successfully uploaded {file.filename}",
        "file_path": str(file_path),
    }
