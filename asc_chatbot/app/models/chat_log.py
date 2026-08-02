from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)  # WhatsApp user phone
    user_message = Column(Text, nullable=False)
    detected_language = Column(String(2), default="en")
    matched_keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=True)
    reply_text = Column(Text, nullable=True)
    reply_media_id = Column(Integer, ForeignKey("media.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    matched_keyword = relationship("Keyword")
    reply_media = relationship("Media")