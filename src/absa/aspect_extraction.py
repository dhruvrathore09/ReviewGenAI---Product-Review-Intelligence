"""Two-stage aspect extraction engine with contextual gating and blacklist enforcement."""

import logging
from typing import Any, Dict, List, Optional
import pandas as pd

from src.absa.aspect_dictionary import (
    COMPILED_ASPECT_PATTERNS,
    is_blacklisted,
)
from src.absa.config import (
    ASPECT_CATEGORIES,
    PRODUCT_ID_COL,
    ROW_ID_COL,
    TIMESTAMP_COL,
    USER_ID_COL,
)
from src.absa.context_analysis import (
    extract_aspect_window,
    split_into_clauses_with_spans,
)

logger = logging.getLogger(__name__)


def extract_aspects_from_text(
    text: str,
    dataset_row_id: int,
    product_id: str,
    user_id: Optional[str] = None,
    review_timestamp: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Extract all valid aspect mentions from review text using clause segmentation and disambiguation.
    
    Args:
        text: Review text (cleaned or raw).
        dataset_row_id: 0-indexed integer position in reviews_processed.csv.
        product_id: Product ASIN or identifier.
        user_id: User identifier if available.
        review_timestamp: Timestamp if available.
        
    Returns:
        List of extracted aspect mention dictionaries.
    """
    clean_text = str(text or "").strip()
    if not clean_text:
        return []

    clauses = split_into_clauses_with_spans(clean_text)
    mentions: List[Dict[str, Any]] = []

    for c_idx, (clause_text, c_start, c_end) in enumerate(clauses):
        # Scan for each candidate aspect category
        for aspect in ASPECT_CATEGORIES:
            pattern = COMPILED_ASPECT_PATTERNS.get(aspect)
            if not pattern:
                continue

            # Stage 1: Anchor match
            match = pattern.search(clause_text)
            if not match:
                continue

            # Stage 2: Disambiguation & blacklist gating
            if is_blacklisted(clause_text, aspect):
                continue

            matched_term = match.group(0)
            m_start = match.start()
            m_end = match.end()

            # Window extraction around the aspect mention
            snippet = extract_aspect_window(clause_text, m_start, m_end)

            mention_record = {
                ROW_ID_COL: int(dataset_row_id),
                PRODUCT_ID_COL: str(product_id),
                USER_ID_COL: str(user_id) if user_id is not None else "",
                TIMESTAMP_COL: int(review_timestamp) if review_timestamp is not None else 0,
                "aspect": aspect,
                "matched_term": matched_term,
                "clause_text": snippet,
                "clause_index": c_idx,
                "start_char": c_start + m_start,
                "end_char": c_start + m_end,
            }
            mentions.append(mention_record)

    return mentions


def extract_aspects_from_dataframe(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract all aspect mentions across the entire dataset.
    
    Args:
        df: Input DataFrame containing processed reviews.
        
    Returns:
        List of all extracted aspect mention dictionaries.
    """
    all_mentions: List[Dict[str, Any]] = []
    text_col = "cleaned_review_text" if "cleaned_review_text" in df.columns else "review_text"

    logger.info("Extracting aspect mentions from %d reviews...", len(df))
    for row_idx, row in df.iterrows():
        review_text = row.get(text_col, "")
        p_id = row.get("product_id", "")
        u_id = row.get("user_id", "")
        ts = row.get("review_timestamp", 0)

        mentions = extract_aspects_from_text(
            text=review_text,
            dataset_row_id=row_idx,
            product_id=p_id,
            user_id=u_id,
            review_timestamp=ts,
        )
        all_mentions.extend(mentions)

    logger.info("Total aspect mentions extracted: %d across %d reviews.", len(all_mentions), len(df))
    return all_mentions
