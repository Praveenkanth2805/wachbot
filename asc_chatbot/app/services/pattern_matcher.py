import re
from typing import List, Tuple, Optional
from app.models import Keyword
from app.models.keyword import MatchType

class PatternMatcher:
    @staticmethod
    def match_pattern(text: str, keyword: Keyword) -> bool:
        pattern = keyword.pattern
        match_type = keyword.match_type
        if match_type == MatchType.exact:
            return text.lower() == pattern.lower()
        elif match_type == MatchType.contains:
            return pattern.lower() in text.lower()
        elif match_type == MatchType.starts:
            return text.lower().startswith(pattern.lower())
        elif match_type == MatchType.ends:
            return text.lower().endswith(pattern.lower())
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
                if kw.priority > best_priority:
                    best_priority = kw.priority
                    best = kw
        return best