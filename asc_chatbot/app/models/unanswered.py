from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class UnansweredMessage(Base):
    __tablename__ = "unanswered_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    language = Column(String(2), default="en")
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())