from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MatchType(str, Enum):
    exact = "exact"
    contains = "contains"
    starts = "starts"
    ends = "ends"
    regex = "regex"

class ResponseType(str, Enum):
    text = "text"
    image = "image"
    pdf = "pdf"
    video = "video"
    audio = "audio"
    document = "document"

# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Keyword schemas
class KeywordBase(BaseModel):
    pattern: str
    match_type: MatchType = MatchType.contains
    priority: int = 0
    language: str = "en"
    is_active: bool = True
    category_id: Optional[int] = None

class KeywordCreate(KeywordBase):
    responses: List["ResponseCreate"] = []

class KeywordUpdate(KeywordBase):
    pass

class Keyword(KeywordBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    category: Optional[Category] = None
    responses: List["Response"] = []

    class Config:
        orm_mode = True

# Response schemas
class ResponseBase(BaseModel):
    type: ResponseType = ResponseType.text
    text: Optional[str] = None
    media_id: Optional[int] = None

class ResponseCreate(ResponseBase):
    pass

class ResponseUpdate(ResponseBase):
    pass

class Response(ResponseBase):
    id: int
    keyword_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    media: Optional["Media"] = None

    class Config:
        orm_mode = True

# Media schemas
class MediaBase(BaseModel):
    filename: str
    original_name: str
    mime_type: str
    size: int
    file_path: str

class MediaCreate(MediaBase):
    pass

class Media(MediaBase):
    id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True

# Chat Log schemas
class ChatLogBase(BaseModel):
    session_id: str
    user_message: str
    detected_language: str = "en"
    matched_keyword_id: Optional[int] = None
    reply_text: Optional[str] = None
    reply_media_id: Optional[int] = None

class ChatLogCreate(ChatLogBase):
    pass

class ChatLog(ChatLogBase):
    id: int
    created_at: datetime
    matched_keyword: Optional[Keyword] = None
    reply_media: Optional[Media] = None

    class Config:
        orm_mode = True

# Unanswered schemas
class UnansweredBase(BaseModel):
    session_id: str
    message: str
    language: str = "en"
    is_resolved: bool = False

class UnansweredCreate(UnansweredBase):
    pass

class Unanswered(UnansweredBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Version schemas
class VersionBase(BaseModel):
    keyword_id: int
    changed_by: Optional[int] = None
    old_text: Optional[str] = None
    new_text: Optional[str] = None
    old_media_id: Optional[int] = None
    new_media_id: Optional[int] = None

class VersionCreate(VersionBase):
    pass

class Version(VersionBase):
    id: int
    changed_at: datetime

    class Config:
        orm_mode = True