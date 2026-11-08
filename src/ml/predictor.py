"""Inference module providing a clean sentiment prediction interface."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np

from src.ml.persistence import load_model, load_pipeline, load_vectorizer

logger = logging.getLogger(__name__)


class SentimentPredictor:
    """Production-ready inference class for sentiment prediction."""

    def __init__(
        self,
        artifact_dir: Optional[Union[str, Path]] = None,
        pipeline_path: Optional[Union[str, Path]] = None,
        model_path: Optional[Union[str, Path]] = None,
        vectorizer_path: Optional[Union[str, Path]] = None,
    ):
        if artifact_dir:
            art_dir = Path(artifact_dir)
            p_path = art_dir / "pipeline.joblib"
            if p_path.exists():
                self.pipeline = load_pipeline(p_path)
                self.model = self.pipeline.named_steps["clf"]
                self.vectorizer = self.pipeline.named_steps["tfidf"]
            else:
                self.model = load_model(art_dir / "model.joblib")
                self.vectorizer = load_vectorizer(art_dir / "vectorizer.joblib")
                self.pipeline = None
        elif pipeline_path:
            self.pipeline = load_pipeline(Path(pipeline_path))
            self.model = self.pipeline.named_steps["clf"]
            self.vectorizer = self.pipeline.named_steps["tfidf"]
        elif model_path and vectorizer_path:
            self.model = load_model(Path(model_path))
            self.vectorizer = load_vectorizer(Path(vectorizer_path))
            self.pipeline = None
        else:
            raise ValueError("Provide either artifact_dir, pipeline_path, or both model_path and vectorizer_path.")

        self.classes_ = list(getattr(self.model, "classes_", []))

    def predict(self, text: str) -> Dict[str, Any]:
        """Predict sentiment label, confidence, and class probabilities for a single text input."""
        cleaned_input = str(text or "").strip()
        if not cleaned_input:
            # Fallback for empty or blank inputs
            default_label = self.classes_[0] if self.classes_ else "neutral"
            return {
                "label": default_label,
                "confidence": 0.0,
                "probabilities": {c: 0.0 for c in self.classes_},
                "is_empty": True,
            }

        # Vectorize text
        X = self.vectorizer.transform([cleaned_input])
        y_pred = self.model.predict(X)[0]

        # Calculate probabilities if supported
        probabilities = {}
        confidence = 1.0
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X)[0]
            probabilities = {
                cls_name: round(float(prob), 4)
                for cls_name, prob in zip(self.classes_, probs)
            }
            confidence = round(float(np.max(probs)), 4)
        elif hasattr(self.model, "decision_function"):
            scores = self.model.decision_function(X)[0]
            confidence = round(float(np.max(np.abs(scores))), 4)

        return {
            "label": str(y_pred),
            "confidence": confidence,
            "probabilities": probabilities,
            "is_empty": False,
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Predict sentiment for a batch of text strings."""
        return [self.predict(t) for t in texts]

