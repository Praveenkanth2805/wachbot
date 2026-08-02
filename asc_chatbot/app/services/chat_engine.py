import re
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import ChatLog, UnansweredMessage
from app.models.response import ResponseType   # ✅ import the Enum
from app.services.pattern_matcher import PatternMatcher
from app.repositories import KeywordRepository
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChatEngine:
    def __init__(self, db: Session):
        self.db = db
        self.keyword_repo = KeywordRepository(db)

    def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        lang = self._detect_language(message)
        keywords = self.keyword_repo.get_active_keywords(language=lang) or self.keyword_repo.get_active_keywords()
        logger.info(f"Keywords loaded: {len(keywords)}")

        matched_keyword = PatternMatcher.find_best_match(message, keywords)
        reply_text = None
        reply_media = None
        matched_kw_id = None

        if matched_keyword:
            matched_kw_id = matched_keyword.id
            logger.info(f"Matched keyword: {matched_keyword.pattern} (id={matched_kw_id}, priority={matched_keyword.priority})")

            full_keyword = self.keyword_repo.get_with_responses(matched_kw_id)
            if full_keyword and full_keyword.responses:
                response = full_keyword.responses[0]
                # ✅ Compare with the Enum value, not the string
                if response.type == ResponseType.text and response.text is not None:
                    reply_text = self._process_dynamic_variables(response.text, session_id)
                elif response.media is not None:
                    reply_media = response.media
                    if response.text:
                        reply_text = self._process_dynamic_variables(response.text, session_id)
                else:
                    logger.warning(f"Response type '{response.type.value}' has no text or media.")
            else:
                logger.warning(f"Keyword {matched_kw_id} has no responses.")

        # Fallback
        if reply_text is None:
            reply_text = settings.FALLBACK_REPLY
            logger.info(f"Using fallback reply: {reply_text}")

        # Save log
        log = ChatLog(
            session_id=session_id,
            user_message=message,
            detected_language=lang,
            matched_keyword_id=matched_kw_id,
            reply_text=reply_text,
            reply_media_id=reply_media.id if reply_media else None
        )
        self.db.add(log)

        if not matched_keyword:
            unans = UnansweredMessage(
                session_id=session_id,
                message=message,
                language=lang
            )
            self.db.add(unans)

        self.db.commit()
        return {
            "text": reply_text,
            "media": reply_media,
            "matched_keyword": matched_keyword,
        }

    def _detect_language(self, text: str) -> str:
        return "ta" if re.search(r'[\u0B80-\u0BFF]', text) else "en"

    def _process_dynamic_variables(self, text: str, session_id: str) -> str:
        return text.replace("{{name}}", session_id).replace("{{time}}", datetime.now().strftime("%Y-%m-%d %H:%M"))