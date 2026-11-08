"""Context-preserving review text and title cleaning module."""

import html
import logging
import re
import unicodedata
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def clean_review_text(text: Optional[str]) -> str:
    """Clean and normalize raw customer review text while strictly preserving context.
    
    Principles:
    1. Preserves ALL negations ('not', 'no', 'never', 'cannot', 'neither', 'nor').
    2. Preserves meaningful punctuation ('.', '!', '?', ',', "'", '-') for sentiment tone.
    3. Preserves numbers and technical specifications (e.g. '1080p', '60Hz', '32GB', '4K').
    4. Normalizes Unicode representations safely (NFKC) without mangling characters.
    5. Strips HTML tags (<br />, <p>, etc.) and unescapes HTML entities.
    6. Normalizes excessive repeated whitespace and punctuation without removing them entirely.
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # 1. Unicode safe normalization (NFKC decomposes compatibility characters safely)
    normalized = unicodedata.normalize("NFKC", text)

    # 2. Unescape HTML entities (e.g. &amp; -> &, &quot; -> ", &#39; -> ')
    normalized = html.unescape(normalized)

    # 3. Strip HTML markup tags (e.g., <br />, <a ...>, <p>)
    normalized = re.sub(r"<[^>]+>", " ", normalized)

    # 4. Normalize raw URLs and web links to preserve sentence structure
    normalized = re.sub(r"https?://\S+|www\.\S+", " ", normalized)

    # 5. Compress extreme repeated punctuation (e.g., '!!!!!' -> '!!', '????' -> '??')
    normalized = re.sub(r"([!?.])\1{2,}", r"\1\1", normalized)

    # 6. Normalize smart quotes and typographic dashes to standard ASCII
    normalized = (
        normalized.replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("–", "-")
        .replace("—", "-")
    )

    # 7. Normalize whitespace (tabs, newlines, multiple spaces -> single space)
    cleaned = re.sub(r"\s+", " ", normalized).strip()

    return cleaned


def clean_review_title(title: Optional[str]) -> str:
    """Clean and normalize review headline/title using a dedicated pipeline."""
    if title is None:
        return ""

    cleaned = clean_review_text(str(title))
    # Strip any trailing boilerplate ellipses, dots, or dangling dashes from headlines
    cleaned = re.sub(r"[\s.\-–—]+$", "", cleaned).strip()
    return cleaned


def clean_reviews_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add cleaned_review_text and cleaned_review_title columns while preserving originals."""
    logger.info("Cleaning reviews dataset (%d records)...", len(df))
    out_df = df.copy()

    # Preserve original review text and title exactly
    out_df["cleaned_review_text"] = out_df["review_text"].apply(clean_review_text)
    out_df["cleaned_review_title"] = out_df["review_title"].apply(clean_review_title)

    logger.info("Review cleaning complete. Original and cleaned text preserved.")
    return out_df
