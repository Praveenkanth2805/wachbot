from app.models import Media
from .base import BaseRepository
from sqlalchemy.orm import Session

class MediaRepository(BaseRepository[Media]):
    def __init__(self, db: Session):
        super().__init__(db, Media)