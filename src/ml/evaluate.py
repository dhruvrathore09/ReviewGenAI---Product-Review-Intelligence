"""Model evaluation module computing performance metrics, confusion matrices, and slice analysis."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Sequence
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

logger = logging.getLogger(__name__)


def evaluate_predictions(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    class_names: Sequence[str],
) -> Dict[str, Any]:
    """Compute classification performance metrics including accuracy, macro/weighted F1, and per-class stats."""
    acc = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
    macro_prec = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    macro_rec = float(recall_score(y_true, y_pred, average="macro", zero_division=0))

    report = classification_report(
        y_true,
        y_pred,
        labels=list(class_names),
        target_names=list(class_names),
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(y_true, y_pred, labels=list(class_names)).tolist()

    per_class = {}
    for cls in class_names:
        if cls in report:
            per_class[cls] = {
                "precision": round(float(report[cls]["precision"]), 4),
                "recall": round(float(report[cls]["recall"]), 4),
                "f1_score": round(float(report[cls]["f1-score"]), 4),
                "support": int(report[cls]["support"]),
            }

    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "per_class": per_class,
        "confusion_matrix": cm,
    }


def evaluate_model(
    model: Any,
    X: Any,
    y_true: Sequence[str],
    class_names: Sequence[str],
) -> Dict[str, Any]:
    """Predict and evaluate model on a feature matrix."""
    y_pred = model.predict(X)
    return evaluate_predictions(y_true, y_pred, class_names)


def perform_slice_analysis(
    model: Any,
    vectorizer: Any,
    df: pd.DataFrame,
    slice_col: str,
    class_names: Sequence[str],
    text_col: str = "full_text",
    target_col: str = "target",
) -> Dict[str, Any]:
    """Perform slice-based error analysis across dataset subpopulations (ml-best-practices)."""
    slice_results = {}
    for slice_val, sub_df in df.groupby(slice_col):
        if len(sub_df) < 5:
            continue
        X_sub = vectorizer.transform(sub_df[text_col])
        metrics = evaluate_model(model, X_sub, sub_df[target_col], class_names)
        slice_results[str(slice_val)] = {
            "sample_size": len(sub_df),
            "macro_f1": metrics["macro_f1"],
            "accuracy": metrics["accuracy"],
            "weighted_f1": metrics["weighted_f1"],
            "per_class": metrics["per_class"],
        }
    return slice_results


def plot_and_save_confusion_matrix(
    cm: List[List[int]],
    class_names: Sequence[str],
    title: str,
    save_path: Path,
) -> Path:
    """Plot and save row-normalized confusion matrix with counts and percentages."""
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    cm_arr = np.array(cm, dtype=float)
    row_sums = cm_arr.sum(axis=1, keepdims=True)
    # Avoid division by zero for empty classes
    row_sums[row_sums == 0] = 1.0
    cm_norm = cm_arr / row_sums

    annot = [
        [f"{int(val)}\n({norm:.1%})" for val, norm in zip(row_val, row_norm)]
        for row_val, row_norm in zip(cm_arr, cm_norm)
    ]

    plt.figure(figsize=(6.5, 5))
    sns.heatmap(
        cm_norm,
        annot=annot,
        fmt="",
        cmap="Blues",
        xticklabels=[c.capitalize() for c in class_names],
        yticklabels=[c.capitalize() for c in class_names],
        cbar=True,
    )
    plt.title(title, fontsize=12, pad=12)
    plt.xlabel("Predicted Class", fontsize=10)
    plt.ylabel("True Class (Support)", fontsize=10)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()

    logger.info("Saved confusion matrix plot to %s", save_path)
    return save_path

