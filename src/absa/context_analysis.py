"""Syntactic clause segmentation, contrast boundary splitting, and negation detection."""

import re
from typing import Dict, List, Tuple

from src.absa.config import (
    COGNITIVE_VERBS,
    CONTRAST_CONJUNCTIONS,
    DIMINISHERS,
    INTENSIFIERS,
    MAX_SNIPPET_LENGTH,
    NEGATION_MARKERS,
    TOKEN_WINDOW_RADIUS,
)

# Sentence boundary regex (splits on ., !, ?, ;, newlines)
SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?;\n])\s+")

# Contrast conjunction regex with word boundary enforcement
_escaped_contrasts = [re.escape(c) for c in sorted(CONTRAST_CONJUNCTIONS, key=len, reverse=True)]
CONTRAST_SPLIT_REGEX = re.compile(
    r"(?:[,–—\-]?\s+)?\b(?:" + "|".join(_escaped_contrasts) + r")\b\s*",
    re.IGNORECASE,
)

# Precompiled negation pattern
_escaped_negations = [re.escape(n) for n in sorted(NEGATION_MARKERS, key=len, reverse=True)]
NEGATION_REGEX = re.compile(r"\b(?:" + "|".join(_escaped_negations) + r")\b", re.IGNORECASE)

# Cognitive matrix verb pattern (for transferred negation / negative raising)
_escaped_cog = [re.escape(v) for v in COGNITIVE_VERBS]
COGNITIVE_NEG_REGEX = re.compile(
    r"\b(don't|do\s+not|doesn't|does\s+not|didn't|did\s+not|can't|cannot)\s+(?:"
    + "|".join(_escaped_cog)
    + r")\b",
    re.IGNORECASE,
)

# Correlative pattern: 'not only ... but ...' (suppresses polarity inversion)
CORRELATIVE_NOT_ONLY_REGEX = re.compile(r"\bnot\s+only\b.*?\bbut\b", re.IGNORECASE)

# Precompiled modifier patterns
_escaped_intensifiers = [re.escape(i) for i in sorted(INTENSIFIERS, key=len, reverse=True)]
INTENSIFIER_REGEX = re.compile(r"\b(?:" + "|".join(_escaped_intensifiers) + r")\b", re.IGNORECASE)

_escaped_diminishers = [re.escape(d) for d in sorted(DIMINISHERS, key=len, reverse=True)]
DIMINISHER_REGEX = re.compile(r"\b(?:" + "|".join(_escaped_diminishers) + r")\b", re.IGNORECASE)


def split_into_clauses_with_spans(text: str) -> List[Tuple[str, int, int]]:
    """Split review text into grammatical sentences and contrastive sub-clauses with character offsets.
    
    Example:
        'Sound quality is excellent, but battery life is disappointing.'
        -> [('Sound quality is excellent', 0, 26), ('battery life is disappointing', 32, 62)]
        
    Args:
        text: Input review text.
        
    Returns:
        List of tuples: (clause_text, start_char, end_char).
    """
    clean_text = str(text or "")
    if not clean_text.strip():
        return []

    clauses: List[Tuple[str, int, int]] = []

    # Step 1: Find sentence spans
    sentence_spans: List[Tuple[int, int]] = []
    last_idx = 0
    for match in SENTENCE_SPLIT_REGEX.finditer(clean_text):
        sentence_spans.append((last_idx, match.start()))
        last_idx = match.end()
    if last_idx < len(clean_text):
        sentence_spans.append((last_idx, len(clean_text)))

    # Step 2: Split compound sentences on contrast boundaries
    for s_start, s_end in sentence_spans:
        sentence_str = clean_text[s_start:s_end]
        if not sentence_str.strip():
            continue

        # Check if sentence contains correlative 'not only ... but ...'
        # If so, do not split on 'but' inside that correlative frame!
        if CORRELATIVE_NOT_ONLY_REGEX.search(sentence_str):
            c_text = sentence_str.strip(" ,–—-:;\t")
            if c_text:
                clauses.append((c_text, s_start, s_end))
            continue

        sub_last = 0
        contrast_matches = list(CONTRAST_SPLIT_REGEX.finditer(sentence_str))
        if not contrast_matches:
            c_text = sentence_str.strip(" ,–—-:;\t")
            if c_text:
                clauses.append((c_text, s_start, s_end))
            continue

        for cm in contrast_matches:
            c_sub = sentence_str[sub_last:cm.start()].strip(" ,–—-:;\t")
            if c_sub:
                clauses.append((c_sub, s_start + sub_last, s_start + cm.start()))
            sub_last = cm.end()

        # Final trailing clause in sentence
        trailing = sentence_str[sub_last:].strip(" ,–—-:;\t")
        if trailing:
            clauses.append((trailing, s_start + sub_last, s_end))

    return clauses if clauses else [(clean_text.strip(), 0, len(clean_text))]


def extract_aspect_window(
    clause: str,
    match_start: int,
    match_end: int,
    window_radius: int = TOKEN_WINDOW_RADIUS,
    max_chars: int = MAX_SNIPPET_LENGTH,
) -> str:
    """Extract a focused local window around the aspect mention to eliminate distant clause noise."""
    if len(clause) <= max_chars:
        return clause.strip()

    pre_text = clause[:match_start]
    post_text = clause[match_end:]

    pre_words = pre_text.split()
    post_words = post_text.split()

    selected_pre = pre_words[-window_radius:] if len(pre_words) > window_radius else pre_words
    selected_post = post_words[:window_radius] if len(post_words) > window_radius else post_words

    matched_term = clause[match_start:match_end]
    windowed = " ".join(selected_pre + [matched_term] + selected_post).strip()
    return windowed[:max_chars]


def find_negation_in_tokens(
    tokens: List[str],
    target_idx: int,
    window_size: int = 3,
) -> Tuple[bool, str]:
    """Check if a negation marker precedes a target token within window_size.
    
    Args:
        tokens: Tokenized list of words.
        target_idx: Index of target word (e.g. sentiment adjective).
        window_size: Preceding window in words.
        
    Returns:
        Tuple of (is_negated, matched_negator).
    """
    start_idx = max(0, target_idx - window_size)
    preceding_tokens = tokens[start_idx:target_idx]

    for token in reversed(preceding_tokens):
        token_clean = token.lower().strip(".,!?:;\"'()")
        if NEGATION_REGEX.fullmatch(token_clean):
            return True, token_clean

    return False, ""


def has_cognitive_negation(clause: str) -> bool:
    """Check if the clause contains negative raising with a cognitive matrix verb.
    
    Example:
        'I don't think the battery life is good.' -> True
    """
    return bool(COGNITIVE_NEG_REGEX.search(clause))


def is_correlative_not_only(clause: str) -> bool:
    """Check if the clause contains correlative 'not only ... but ...' addition."""
    return bool(CORRELATIVE_NOT_ONLY_REGEX.search(clause))


def detect_modifiers(tokens: List[str], target_idx: int, window_size: int = 2) -> Dict[str, bool]:
    """Detect presence of intensifiers or diminishers modifying the target word."""
    start_idx = max(0, target_idx - window_size)
    preceding = tokens[start_idx:target_idx]

    has_intensifier = any(bool(INTENSIFIER_REGEX.fullmatch(t.lower().strip(".,!?:;\"'()"))) for t in preceding)
    has_diminisher = any(bool(DIMINISHER_REGEX.fullmatch(t.lower().strip(".,!?:;\"'()"))) for t in preceding)

    return {
        "has_intensifier": has_intensifier,
        "has_diminisher": has_diminisher,
    }


def has_negation_marker(text: str) -> bool:
    """Check if any negation marker exists in the text string."""
    return bool(NEGATION_REGEX.search(text))
