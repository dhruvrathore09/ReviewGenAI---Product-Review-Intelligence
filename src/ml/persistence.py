"""Model and artifact persistence module for serialization and deserialization."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Sequence, Tuple
import joblib
from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

from src.ml.evaluate import plot_and_save_confusion_matrix
from src.ml.vectorizer import load_vectorizer, save_vectorizer

logger = logging.getLogger(__name__)


def save_model(model: BaseEstimator, path: Path) -> Path:
    """Serialize trained classifier model."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    logger.info("Saved classifier model to %s", path)
    return path


def load_model(path: Path) -> BaseEstimator:
    """Load serialized classifier model."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found at '{path}'")
    return joblib.load(path)


def save_pipeline(vectorizer: TfidfVectorizer, model: BaseEstimator, path: Path) -> Path:
    """Create and serialize end-to-end Pipeline taking raw text directly to predictions."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pipe = Pipeline([
        ("tfidf", vectorizer),
        ("clf", model),
    ])
    joblib.dump(pipe, path)
    logger.info("Saved unified Pipeline to %s", path)
    return path


def load_pipeline(path: Path) -> Pipeline:
    """Load unified Pipeline."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Pipeline file not found at '{path}'")
    return joblib.load(path)


def save_experiment_artifacts(
    output_dir: Path,
    model: BaseEstimator,
    vectorizer: TfidfVectorizer,
    metrics: Dict[str, Any],
    class_names: Sequence[str],
    experiment_title: str,
) -> Dict[str, Path]:
    """Serialize all artifacts for an experiment into a dedicated directory.
    
    Artifacts Saved:
    - model.joblib: Standalone trained classifier
    - vectorizer.joblib: Standalone fitted TF-IDF vectorizer
    - pipeline.joblib: Unified end-to-end Pipeline
    - metrics.json: Complete evaluation benchmarks and slice analysis
    - confusion_matrix.png: Visual confusion matrix heatmap
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model_path = save_model(model, out_dir / "model.joblib")
    vectorizer_path = out_dir / "vectorizer.joblib"
    joblib.dump(vectorizer, vectorizer_path)
    pipeline_path = save_pipeline(vectorizer, model, out_dir / "pipeline.joblib")

    # Save metrics JSON (excluding Python model/vectorizer objects)
    clean_metrics = {
        k: v for k, v in metrics.items() if k not in ("best_model", "vectorizer")
    }
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(clean_metrics, f, indent=2)
    logger.info("Saved evaluation metrics to %s", metrics_path)

    # Plot and save confusion matrix for the winning model's holdout test evaluation
    test_res = metrics.get("holdout_test_metrics") or metrics.get("test_metrics") or {}
    cm = test_res.get("confusion_matrix")
    if cm is not None:
        cm_path = plot_and_save_confusion_matrix(
            cm=cm,
            class_names=class_names,
            title=f"Confusion Matrix (Holdout): {experiment_title}",
            save_path=out_dir / "confusion_matrix.png",
        )
    else:
        cm_path = None

    return {
        "model": model_path,
        "vectorizer": vectorizer_path,
        "pipeline": pipeline_path,
        "metrics": metrics_path,
        "confusion_matrix": cm_path,
    }
