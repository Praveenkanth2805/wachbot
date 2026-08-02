from app.models import Keyword
from .base import BaseRepository
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List

class KeywordRepository(BaseRepository[Keyword]):
    def __init__(self, db: Session):
        super().__init__(db, Keyword)

    def get_with_responses(self, id: int) -> Optional[Keyword]:
        return self.db.query(Keyword).options(joinedload(Keyword.responses)).filter(Keyword.id == id).first()

    def get_active_keywords(self, language: Optional[str] = None) -> List[Keyword]:
        query = self.db.query(Keyword).filter(Keyword.is_active == True)
        if language:
            query = query.filter(Keyword.language == language)
        return query.all()