from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class MatchType(enum.Enum):
    exact = "exact"
    contains = "contains"
    starts = "starts"
    ends = "ends"
    regex = "regex"

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String, nullable=False, index=True)
    match_type = Column(Enum(MatchType), default=MatchType.contains)
    priority = Column(Integer, default=0)
    language = Column(String(2), default="en")
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category")
    responses = relationship("Response", back_populates="keyword", cascade="all, delete-orphan")