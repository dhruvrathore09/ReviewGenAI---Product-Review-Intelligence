"""Data loader module for streaming reviews and fetching product metadata."""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pandas as pd
import pyarrow.parquet as pq
import requests

from src.config import (
    LOCAL_META_CACHE,
    META_RAW_FIELDS,
    META_SHARD_URL,
    REVIEW_STREAM_URL,
)

logger = logging.getLogger(__name__)


def ensure_metadata_shard(
    shard_url: str = META_SHARD_URL,
    local_path: Path = LOCAL_META_CACHE,
    chunk_size: int = 1024 * 1024,
) -> Path:
    """Ensures the regional metadata shard parquet file exists locally.
    
    If not already present in the cache, streams and saves the shard file.
    """
    local_path = Path(local_path)
    if local_path.exists() and local_path.stat().st_size > 0:
        logger.info(f"Using cached metadata shard at: {local_path} ({local_path.stat().st_size / (1024*1024):.2f} MB)")
        return local_path

    local_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Downloading product metadata shard from {shard_url}...")
    start_time = time.time()
    
    with requests.get(shard_url, stream=True) as response:
        response.raise_for_status()
        total_bytes = 0
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    total_bytes += len(chunk)
                    if total_bytes % (20 * 1024 * 1024) < chunk_size:
                        logger.info(f"Downloaded {total_bytes / (1024*1024):.1f} MB in {time.time() - start_time:.1f}s...")

    logger.info(
        f"Metadata shard successfully downloaded: {total_bytes / (1024*1024):.2f} MB in {time.time() - start_time:.2f}s."
    )
    return local_path


def load_product_catalog(
    local_parquet_path: Path = LOCAL_META_CACHE,
) -> Tuple[pd.DataFrame, Set[str]]:
    """Loads the product catalog parquet file into a pandas DataFrame.
    
    Returns:
        Tuple of (meta_df, set_of_parent_asins).
    """
    logger.info(f"Loading product metadata from {local_parquet_path}...")
    start_time = time.time()
    table = pq.read_table(local_parquet_path, columns=META_RAW_FIELDS)
    meta_df = table.to_pandas()
    valid_asins = set(meta_df["parent_asin"].dropna().unique())
    logger.info(
        f"Loaded {len(meta_df):,} product records with {len(valid_asins):,} unique ASINs in {time.time() - start_time:.2f}s."
    )
    return meta_df, valid_asins


def stream_customer_reviews(
    review_stream_url: str = REVIEW_STREAM_URL,
    valid_asins: Set[str] = None,
    target_count: int = 8000,
    max_scan_lines: int = 100000,
) -> List[Dict]:
    """Streams reviews incrementally from the raw JSONL endpoint without downloading the entire 21GB dataset.
    
    Args:
        review_stream_url: URL to the remote JSONL file.
        valid_asins: Set of product parent_asins to match for metadata.
        target_count: Desired number of matched raw reviews to collect.
        max_scan_lines: Safety cap on number of lines scanned.

    Returns:
        List of raw review dictionaries.
    """
    logger.info(
        f"Connecting to review stream at {review_stream_url} (target: {target_count:,} reviews)..."
    )
    start_time = time.time()
    collected_reviews: List[Dict] = []
    scanned_lines = 0

    with requests.get(review_stream_url, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue

            scanned_lines += 1
            record = json.loads(line.decode("utf-8"))
            parent_asin = record.get("parent_asin")

            if valid_asins is None or parent_asin in valid_asins:
                collected_reviews.append(record)
                if len(collected_reviews) >= target_count:
                    break

            if scanned_lines % 10000 == 0:
                elapsed = time.time() - start_time
                logger.info(
                    f"Scanned {scanned_lines:,} lines | Collected {len(collected_reviews):,} reviews "
                    f"({scanned_lines / elapsed:.1f} lines/sec)..."
                )

            if scanned_lines >= max_scan_lines:
                logger.warning(
                    f"Reached max scan limit ({max_scan_lines:,} lines) with {len(collected_reviews):,} reviews."
                )
                break

    elapsed_total = time.time() - start_time
    logger.info(
        f"Streaming completed: Collected {len(collected_reviews):,} reviews by scanning "
        f"{scanned_lines:,} lines in {elapsed_total:.2f}s ({scanned_lines / max(elapsed_total, 0.001):.1f} lines/sec)."
    )
    return collected_reviews

