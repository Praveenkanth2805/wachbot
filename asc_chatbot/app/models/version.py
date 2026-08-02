from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    old_text = Column(Text, nullable=True)
    new_text = Column(Text, nullable=True)
    old_media_id = Column(Integer, ForeignKey("media.id"), nullable=True)
    new_media_id = Column(Integer, ForeignKey("media.id"), nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())