"""Model training, candidate benchmarking, and experiment execution module."""

import logging
from typing import Any, Dict, Sequence
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer

from src.ml.config import FEATURE_COL
from src.ml.evaluate import evaluate_model, perform_slice_analysis
from src.ml.models import get_candidate_models
from src.ml.vectorizer import create_vectorizer, fit_vectorizer, transform_texts

logger = logging.getLogger(__name__)


def train_and_benchmark(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    class_names: Sequence[str],
    experiment_name: str,
    text_col: str = FEATURE_COL,
) -> Dict[str, Any]:
    """Train candidate models, benchmark strictly against validation split, and evaluate ONLY the selected winner on holdout.
    
    Rigorous Evaluation Protocol:
    1. Strict Featurization Ordering: TF-IDF vectorizer is fitted ONLY on train_df[text_col].
    2. Model Comparison Protocol: All candidate models are trained on train_df and benchmarked
       EXCLUSIVELY on val_df. Candidate models NEVER touch the final test holdout.
    3. Model Selection: The optimal model is selected strictly using Validation Macro F1.
    4. Sealed Holdout Evaluation: The fresh test holdout is evaluated ONCE, strictly on the
       single winning model, preserving holdout integrity.
    
    Args:
        train_df: Stratified training split.
        val_df: Stratified validation split for model comparison and selection.
        test_df: Sealed, untouched holdout split for final evaluation only.
        class_names: Target classes.
        experiment_name: Label for the experiment run.
        text_col: Feature column name for text TF-IDF extraction (default: 'cleaned_review_text').
        
    Returns:
        Dictionary containing validation benchmarks, best model, vectorizer, and holdout metrics.
    """
    logger.info("================================================================================")
    logger.info("STARTING EXPERIMENT: %s", experiment_name)
    logger.info(
        "Splits: Train=%d, Val=%d, Holdout Test=%d | Classes: %s | Feature: '%s' ONLY",
        len(train_df),
        len(val_df),
        len(test_df),
        class_names,
        text_col,
    )
    logger.info("================================================================================")

    # 1. Strict Featurization Ordering: Fit vectorizer ONLY on training texts
    vectorizer = create_vectorizer()
    vectorizer = fit_vectorizer(vectorizer, train_df[text_col])

    X_train = transform_texts(vectorizer, train_df[text_col])
    X_val = transform_texts(vectorizer, val_df[text_col])

    y_train = np.array(train_df["target"].tolist(), dtype=str)
    y_val = np.array(val_df["target"].tolist(), dtype=str)
    y_test = np.array(test_df["target"].tolist(), dtype=str)

    # 2. Benchmark candidate models EXCLUSIVELY on Validation Data
    candidate_models = get_candidate_models()
    validation_benchmarks = {}
    best_model_name = None
    best_val_macro_f1 = -1.0
    best_model = None

    for name, model in candidate_models.items():
        logger.info("Training candidate model: '%s' on %d training samples...", name, len(train_df))
        model.fit(X_train, y_train)

        # Evaluate strictly on validation split
        val_metrics = evaluate_model(model, X_val, y_val, class_names)

        validation_benchmarks[name] = {
            "validation_metrics": val_metrics,
        }

        logger.info(
            "[%s] Validation Macro F1: %.4f | Weighted F1: %.4f | Accuracy: %.4f",
            name,
            val_metrics["macro_f1"],
            val_metrics["weighted_f1"],
            val_metrics["accuracy"],
        )

        # Model Selection: select best model based on Validation Macro F1
        if val_metrics["macro_f1"] > best_val_macro_f1:
            best_val_macro_f1 = val_metrics["macro_f1"]
            best_model_name = name
            best_model = model

    logger.info(
        "--> Optimal Model Selected via Validation Macro F1: '%s' (Val Macro F1: %.4f)",
        best_model_name,
        best_val_macro_f1,
    )

    # 3. Sealed Holdout Evaluation: Evaluate ONLY the selected winning model on test_df
    logger.info("Unsealing Holdout Test Set for final evaluation of winning model '%s'...", best_model_name)
    X_test_holdout = transform_texts(vectorizer, test_df[text_col])
    holdout_test_metrics = evaluate_model(best_model, X_test_holdout, y_test, class_names)

    logger.info(
        "[%s - Final Holdout Test] Macro F1: %.4f | Weighted F1: %.4f | Accuracy: %.4f",
        best_model_name,
        holdout_test_metrics["macro_f1"],
        holdout_test_metrics["weighted_f1"],
        holdout_test_metrics["accuracy"],
    )

    # 4. Slice-Based Error Analysis on Holdout using ONLY the selected model
    logger.info("Performing slice-based error analysis on holdout using winning model '%s'...", best_model_name)
    test_eval_df = test_df.copy()

    # Slice A: Verified vs Unverified Purchase
    if "is_verified_purchase" in test_eval_df.columns:
        test_eval_df["verified_slice"] = np.where(
            test_eval_df["is_verified_purchase"].astype(str).str.lower().isin(["true", "1"]),
            "Verified Purchase",
            "Unverified Purchase",
        )
        verified_slice = perform_slice_analysis(
            best_model, vectorizer, test_eval_df, "verified_slice", class_names, text_col=text_col
        )
    else:
        verified_slice = {}

    # Slice B: Short vs Long Reviews
    if "review_word_count" in test_eval_df.columns:
        test_eval_df["length_slice"] = np.where(
            test_eval_df["review_word_count"] < 30,
            "Short (<30 words)",
            "Long (>=30 words)",
        )
        length_slice = perform_slice_analysis(
            best_model, vectorizer, test_eval_df, "length_slice", class_names, text_col=text_col
        )
    else:
        length_slice = {}

    return {
        "experiment_name": experiment_name,
        "input_feature": text_col,
        "class_names": list(class_names),
        "split_counts": {
            "train": len(train_df),
            "validation": len(val_df),
            "holdout_test": len(test_df),
        },
        "best_model_name": best_model_name,
        "best_model": best_model,
        "vectorizer": vectorizer,
        "validation_macro_f1": best_val_macro_f1,
        "candidate_benchmarks": validation_benchmarks,
        "holdout_test_metrics": holdout_test_metrics,
        "slice_analysis": {
            "verified_purchase": verified_slice,
            "review_length": length_slice,
        },
    }
