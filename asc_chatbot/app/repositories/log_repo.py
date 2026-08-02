from app.models import ChatLog, UnansweredMessage
from .base import BaseRepository
from sqlalchemy.orm import Session

class ChatLogRepository(BaseRepository[ChatLog]):
    def __init__(self, db: Session):
        super().__init__(db, ChatLog)

class UnansweredRepository(BaseRepository[UnansweredMessage]):
    def __init__(self, db: Session):
        super().__init__(db, UnansweredMessage)