from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class ResponseType(enum.Enum):
    text = "text"
    image = "image"
    pdf = "pdf"
    video = "video"
    audio = "audio"
    document = "document"

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    type = Column(Enum(ResponseType), default=ResponseType.text)
    text = Column(Text, nullable=True)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    keyword = relationship("Keyword", back_populates="responses")
    media = relationship("Media")