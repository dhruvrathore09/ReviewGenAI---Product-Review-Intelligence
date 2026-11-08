"""Candidate classification models definition and factory."""

from typing import Dict
from sklearn.base import BaseEstimator
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from src.ml.config import RANDOM_STATE


def get_candidate_models(random_state: int = RANDOM_STATE) -> Dict[str, BaseEstimator]:
    """Instantiate the 4 candidate classification models for sentiment benchmarking.
    
    Models:
    1. DummyClassifier: Naive majority-class baseline to establish performance floor.
    2. MultinomialNB: Fast generative baseline with Laplace smoothing (alpha=0.5).
    3. Logistic Regression: Linear model with balanced class weights to address 81.8% positive imbalance.
    4. Calibrated Linear SVM: Linear Support Vector Classifier with balanced weights, calibrated via
       Platt scaling / sigmoid cross-validation (cv=3) to provide reliable probability estimates.
    """
    return {
        "Dummy Baseline": DummyClassifier(strategy="most_frequent"),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.5),
        "Logistic Regression (Balanced)": LogisticRegression(
            class_weight="balanced",
            C=1.0,
            max_iter=1000,
            random_state=random_state,
        ),
        "Calibrated Linear SVM": CalibratedClassifierCV(
            estimator=LinearSVC(
                class_weight="balanced",
                C=1.0,
                random_state=random_state,
            ),
            cv=3,
        ),
    }

