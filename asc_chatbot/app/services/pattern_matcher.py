import re
from typing import List, Optional
from app.models import Keyword
from app.models.keyword import MatchType
import logging

logger = logging.getLogger(__name__)

class PatternMatcher:
    @staticmethod
    def match_pattern(text: str, keyword: Keyword) -> bool:
        pattern = keyword.pattern
        match_type = keyword.match_type
        text_lower = text.lower().strip()
        pattern_lower = pattern.lower().strip()
        if match_type == MatchType.exact:
            return text_lower == pattern_lower
        elif match_type == MatchType.contains:
            return pattern_lower in text_lower
        elif match_type == MatchType.starts:
            return text_lower.startswith(pattern_lower)
        elif match_type == MatchType.ends:
            return text_lower.endswith(pattern_lower)
        elif match_type == MatchType.regex:
            try:
                return re.search(pattern, text, re.IGNORECASE) is not None
            except:
                return False
        return False

    @staticmethod
    def find_best_match(text: str, keywords: List[Keyword]) -> Optional[Keyword]:
        best = None
        best_priority = -1
        for kw in keywords:
            if PatternMatcher.match_pattern(text, kw):
                logger.debug(f"Matched: {kw.pattern} (priority {kw.priority})")
                if kw.priority > best_priority:
                    best_priority = kw.priority
                    best = kw
        return best