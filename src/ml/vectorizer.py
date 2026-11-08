"""TF-IDF vectorization module for n-gram feature extraction."""

import logging
from pathlib import Path
from typing import Iterable, Optional, Tuple
import joblib
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

from src.ml.config import (
    TFIDF_MAX_FEATURES,
    TFIDF_MIN_DF,
    TFIDF_NGRAM_RANGE,
    TFIDF_SUBLINEAR_TF,
)

logger = logging.getLogger(__name__)


def create_vectorizer(
    max_features: int = TFIDF_MAX_FEATURES,
    ngram_range: Tuple[int, int] = TFIDF_NGRAM_RANGE,
    sublinear_tf: bool = TFIDF_SUBLINEAR_TF,
    min_df: int = TFIDF_MIN_DF,
) -> TfidfVectorizer:
    """Instantiate a TF-IDF vectorizer configured for sentiment text.
    
    Design Choices:
    - ngram_range=(1, 2): Captures both unigrams ('good', 'defective') and bigrams
      ('not working', 'great sound', 'stopped charging'), which are vital for polarity.
    - sublinear_tf=True: Replaces TF with 1 + log(TF), dampening the influence of repeated words.
    - stop_words=None: Crucial! Default English stop words strip 'not', 'no', 'never', 'cannot',
      which completely inverts sentiment semantics.
    """
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        sublinear_tf=sublinear_tf,
        min_df=min_df,
        stop_words=None,
        token_pattern=r"(?u)\b\w+\b",
    )


def fit_vectorizer(
    vectorizer: TfidfVectorizer,
    train_texts: Iterable[str],
) -> TfidfVectorizer:
    """Fit TF-IDF vocabulary strictly on training texts (no data leakage)."""
    logger.info("Fitting TF-IDF vectorizer on %d training texts...", len(list(train_texts)))
    vectorizer.fit(train_texts)
    logger.info("Vectorizer fitted. Vocabulary size: %d terms.", len(vectorizer.vocabulary_))
    return vectorizer


def transform_texts(
    vectorizer: TfidfVectorizer,
    texts: Iterable[str],
) -> csr_matrix:
    """Transform texts into TF-IDF sparse document-term matrix."""
    return vectorizer.transform(texts)


def save_vectorizer(vectorizer: TfidfVectorizer, path: Path) -> Path:
    """Serialize fitted vectorizer artifact."""
    save_path = Path(path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, save_path)
    logger.info("Saved fitted vectorizer to %s", save_path)
    return save_path


def load_vectorizer(path: Path) -> TfidfVectorizer:
    """Load serialized vectorizer artifact."""
    load_path = Path(path)
    if not load_path.exists():
        raise FileNotFoundError(f"Vectorizer file not found at '{load_path}'")
    return joblib.load(load_path)

