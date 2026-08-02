import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from app.core.config import settings
from app.models import Media
from app.repositories import MediaRepository
from sqlalchemy.orm import Session
import uuid
import mimetypes

class MediaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MediaRepository(db)
        self.media_root = Path(settings.MEDIA_ROOT)

    def save_file(self, file: UploadFile, subdir: str = "documents") -> Media:
        # Determine subdirectory based on mime type
        mime_type = file.content_type or "application/octet-stream"
        if mime_type.startswith("image/"):
            subdir = "images"
        elif mime_type == "application/pdf":
            subdir = "pdfs"
        elif mime_type.startswith("video/"):
            subdir = "videos"
        elif mime_type.startswith("audio/"):
            subdir = "audio"

        upload_path = self.media_root / subdir
        upload_path.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        ext = Path(file.filename).suffix
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = upload_path / filename

        # Save file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Store in DB
        media = Media(
            filename=filename,
            original_name=file.filename,
            mime_type=mime_type,
            size=file.size or 0,
            file_path=str(file_path.relative_to(self.media_root))
        )
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media

    def delete_file(self, media_id: int) -> bool:
        media = self.repo.get(media_id)
        if not media:
            return False
        # Delete physical file
        full_path = self.media_root / media.file_path
        if full_path.exists():
            full_path.unlink()
        # Delete DB record
        self.repo.delete(media_id)
        return True

    def get_file_path(self, media: Media) -> Path:
        return self.media_root / media.file_path