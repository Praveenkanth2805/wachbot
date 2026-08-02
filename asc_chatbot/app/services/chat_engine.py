from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Keyword, Response, Media, ChatLog, UnansweredMessage
from app.services.pattern_matcher import PatternMatcher
from app.repositories import KeywordRepository, ChatLogRepository, UnansweredRepository
from app.core.config import settings
import logging
import re

logger = logging.getLogger(__name__)

class ChatEngine:
    def __init__(self, db: Session):
        self.db = db
        self.keyword_repo = KeywordRepository(db)
        self.chat_log_repo = ChatLogRepository(db)
        self.unanswered_repo = UnansweredRepository(db)

    def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        # Detect language (simple: check for Tamil unicode range)
        lang = self._detect_language(message)
        # Fetch active keywords for that language
        keywords = self.keyword_repo.get_active_keywords(language=lang)
        if not keywords:
            keywords = self.keyword_repo.get_active_keywords()  # fallback to all

        matched_keyword = PatternMatcher.find_best_match(message, keywords)

        reply_text = None
        reply_media = None
        matched_kw_id = None

        if matched_keyword:
            matched_kw_id = matched_keyword.id
            # Get responses for this keyword
            responses = matched_keyword.responses
            if responses:
                # Pick first response (or implement selection logic)
                response = responses[0]
                if response.type == "text":
                    reply_text = self._process_dynamic_variables(response.text or "", session_id)
                elif response.media:
                    reply_media = response.media
                    # if media is attached, we can also send text if any
                    if response.text:
                        reply_text = self._process_dynamic_variables(response.text, session_id)

        # Log
        log = ChatLog(
            session_id=session_id,
            user_message=message,
            detected_language=lang,
            matched_keyword_id=matched_kw_id,
            reply_text=reply_text,
            reply_media_id=reply_media.id if reply_media else None
        )
        self.chat_log_repo.create(**log.__dict__)

        if not matched_keyword:
            # Unanswered
            unans = UnansweredMessage(
                session_id=session_id,
                message=message,
                language=lang
            )
            self.unanswered_repo.create(**unans.__dict__)
            # Fallback reply
            reply_text = settings.FALLBACK_REPLY

        return {
            "text": reply_text,
            "media": reply_media,
            "matched_keyword": matched_keyword,
        }

    def _detect_language(self, text: str) -> str:
        # Simple detection: if any Tamil character, return 'ta'
        if re.search(r'[\u0B80-\u0BFF]', text):
            return "ta"
        return "en"

    def _process_dynamic_variables(self, text: str, session_id: str) -> str:
        # Replace {{name}} with something (we don't have name, use session_id)
        # In future, fetch from WhatsApp profile
        # For now, just return as is
        return text.replace("{{name}}", session_id).replace("{{time}}", str(datetime.now()))