from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from app.database import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)  # stored filename
    original_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    file_path = Column(String, nullable=False)  # relative path from MEDIA_ROOT
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())