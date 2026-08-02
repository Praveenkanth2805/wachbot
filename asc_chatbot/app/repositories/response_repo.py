from app.models import Response
from .base import BaseRepository
from sqlalchemy.orm import Session

class ResponseRepository(BaseRepository[Response]):
    def __init__(self, db: Session):
        super().__init__(db, Response)