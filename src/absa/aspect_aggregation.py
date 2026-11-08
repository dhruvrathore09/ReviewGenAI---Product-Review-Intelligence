"""Aggregation module compiling review-level and product-level aspect analytics."""

from typing import Any, Dict, List
import pandas as pd

from src.absa.config import (
    ASPECT_CATEGORIES,
    PRODUCT_ID_COL,
    ROW_ID_COL,
    SENTIMENT_NEGATIVE,
    SENTIMENT_NEUTRAL,
    SENTIMENT_POSITIVE,
    SENTIMENT_UNCERTAIN,
    TIMESTAMP_COL,
    USER_ID_COL,
)


def aggregate_review_level_results(
    reviews_df: pd.DataFrame,
    mentions: List[Dict[str, Any]],
) -> pd.DataFrame:
    """Aggregate individual aspect mentions into a unified review-level DataFrame.
    
    Guarantees that every review in reviews_df (all 7,991 rows) has a corresponding record.
    """
    mentions_df = pd.DataFrame(mentions) if mentions else pd.DataFrame()

    results = []
    text_col = "cleaned_review_text" if "cleaned_review_text" in reviews_df.columns else "review_text"

    for row_idx, row in reviews_df.iterrows():
        p_id = row.get("product_id", "")
        u_id = row.get("user_id", "")
        ts = row.get("review_timestamp", 0)

        record = {
            ROW_ID_COL: row_idx,
            PRODUCT_ID_COL: p_id,
            USER_ID_COL: u_id,
            TIMESTAMP_COL: ts,
            "has_aspects": False,
            "detected_aspects": "",
            "battery_sentiment": "not_mentioned",
            "sound_sentiment": "not_mentioned",
            "build_sentiment": "not_mentioned",
            "display_sentiment": "not_mentioned",
            "price_sentiment": "not_mentioned",
        }

        if not mentions_df.empty and ROW_ID_COL in mentions_df.columns:
            m_sub = mentions_df[mentions_df[ROW_ID_COL] == row_idx]
            if not m_sub.empty:
                record["has_aspects"] = True
                unique_aspects = sorted(m_sub["aspect"].unique().tolist())
                record["detected_aspects"] = "|".join(unique_aspects)

                for asp in unique_aspects:
                    asp_mentions = m_sub[m_sub["aspect"] == asp]
                    # Select dominant sentiment or highest confidence
                    dominant = asp_mentions.sort_values(by="confidence", ascending=False).iloc[0]["sentiment"]
                    if asp == "battery":
                        record["battery_sentiment"] = dominant
                    elif asp == "sound_quality":
                        record["sound_sentiment"] = dominant
                    elif asp == "build_quality":
                        record["build_sentiment"] = dominant
                    elif asp == "display":
                        record["display_sentiment"] = dominant
                    elif asp == "price_value":
                        record["price_sentiment"] = dominant

        results.append(record)

    return pd.DataFrame(results)


def aggregate_product_level_summary(
    mentions: List[Dict[str, Any]],
) -> pd.DataFrame:
    """Aggregate aspect mentions by product and category to produce product intelligence profiles."""
    if not mentions:
        return pd.DataFrame(
            columns=[
                PRODUCT_ID_COL,
                "aspect",
                "total_mentions",
                "positive_mentions",
                "neutral_mentions",
                "negative_mentions",
                "uncertain_mentions",
                "net_sentiment_score",
                "positive_ratio",
                "top_positive_snippet",
                "top_negative_snippet",
            ]
        )

    mentions_df = pd.DataFrame(mentions)
    summary_rows = []

    grouped = mentions_df.groupby([PRODUCT_ID_COL, "aspect"])

    for (p_id, aspect), group in grouped:
        total = len(group)
        pos = int((group["sentiment"] == SENTIMENT_POSITIVE).sum())
        neu = int((group["sentiment"] == SENTIMENT_NEUTRAL).sum())
        neg = int((group["sentiment"] == SENTIMENT_NEGATIVE).sum())
        unc = int((group["sentiment"] == SENTIMENT_UNCERTAIN).sum())

        net_score = round((pos - neg) / total, 2) if total > 0 else 0.0
        pos_ratio = round(pos / total, 2) if total > 0 else 0.0

        # Extract representative snippets
        pos_group = group[group["sentiment"] == SENTIMENT_POSITIVE].sort_values(by="confidence", ascending=False)
        top_pos = pos_group.iloc[0]["clause_text"] if not pos_group.empty else ""

        neg_group = group[group["sentiment"] == SENTIMENT_NEGATIVE].sort_values(by="confidence", ascending=False)
        top_neg = neg_group.iloc[0]["clause_text"] if not neg_group.empty else ""

        summary_rows.append({
            PRODUCT_ID_COL: p_id,
            "aspect": aspect,
            "total_mentions": total,
            "positive_mentions": pos,
            "neutral_mentions": neu,
            "negative_mentions": neg,
            "uncertain_mentions": unc,
            "net_sentiment_score": net_score,
            "positive_ratio": pos_ratio,
            "top_positive_snippet": top_pos,
            "top_negative_snippet": top_neg,
        })

    summary_df = pd.DataFrame(summary_rows)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(by=[PRODUCT_ID_COL, "total_mentions"], ascending=[True, False]).reset_index(drop=True)
    return summary_df
