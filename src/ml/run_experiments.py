"""Top-level CLI runner executing Level 5 Sentiment Analysis experiments end-to-end under strict protocol."""

import json
import logging
import sys
import time
from pathlib import Path

from src.ml.config import (
    BINARY_CLASSES,
    EXP_A_DIR,
    EXP_B_DIR,
    FEATURE_COL,
    MODELS_DIR,
    REPORTS_DIR,
    SPLIT_RANDOM_STATE,
    THREE_CLASSES,
)
from src.ml.dataset import load_processed_reviews, prepare_dataset
from src.ml.persistence import save_experiment_artifacts
from src.ml.split import split_dataset
from src.ml.train import train_and_benchmark

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def generate_markdown_report(
    exp_a_res: dict,
    exp_b_res: dict,
    output_path: Path,
) -> Path:
    """Generate comprehensive markdown evaluation report with benchmark tables and findings."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Level 5: Sentiment Analysis Model Evaluation Report",
        "",
        "**Project:** Product Review Intelligence Platform  ",
        "**Milestone:** Level 5 — Sentiment Analysis using Machine Learning  ",
        "**Protocol:** Strict Dataset Contract Compliance & Sealed Holdout Evaluation  ",
        "**Input Feature:** `cleaned_review_text` STRICTLY (titles & metadata excluded)  ",
        f"**Fresh Holdout Random Seed:** `{SPLIT_RANDOM_STATE}`  ",
        "",
        "---",
        "",
        "## 1. Executive Summary & Experimental Protocol",
        "",
        "Level 5 evaluates machine learning models on customer reviews from the Amazon Reviews 2023 Electronics dataset under a strict experimental protocol:",
        "",
        "1. **Input Feature Isolation**: Models are trained **strictly on `cleaned_review_text`**. Review titles, IDs, product metadata, and numerical ratings are strictly excluded from TF-IDF feature extraction to guarantee zero target leakage.",
        "2. **Strict Model Selection Protocol**: Candidate models are trained on the Training set and compared **strictly on the Validation set** using **Validation Macro F1**. The test holdout is never touched during model comparison.",
        "3. **Independent Holdout Evaluation**: A fresh, sealed holdout test set (15%) is established and evaluated **strictly on the single selected winning model** once selection is final.",
        "4. **Weak-Supervision Proxy Labels**: Target labels are derived directly from customer `star_rating` as heuristic proxy labels (1-2: negative, 3: neutral, 4-5: positive).",
        "",
        "---",
        "",
        "## 2. Dataset Split Distributions",
        "",
        "In compliance with `ml-best-practices`, **Strict Featurization Ordering** was enforced: datasets were split into stratified Train (70%), Validation (15%), and Holdout Test (15%) splits **before** TF-IDF vocabulary fitting.",
        "",
        "### Experiment A (Binary) Split Counts (3-Star Reviews Excluded)",
        f"- **Total Reviews:** {exp_a_res['split_counts']['train'] + exp_a_res['split_counts']['validation'] + exp_a_res['split_counts']['holdout_test']:,}",
        f"- **Train Set (70%):** {exp_a_res['split_counts']['train']:,} samples",
        f"- **Validation Set (15%):** {exp_a_res['split_counts']['validation']:,} samples (used for candidate comparison)",
        f"- **Holdout Test Set (15%):** {exp_a_res['split_counts']['holdout_test']:,} samples (evaluated strictly on winner)",
        "",
        "### Experiment B (Three-Class) Split Counts (All Reviews Included)",
        f"- **Total Reviews:** {exp_b_res['split_counts']['train'] + exp_b_res['split_counts']['validation'] + exp_b_res['split_counts']['holdout_test']:,}",
        f"- **Train Set (70%):** {exp_b_res['split_counts']['train']:,} samples",
        f"- **Validation Set (15%):** {exp_b_res['split_counts']['validation']:,} samples (used for candidate comparison)",
        f"- **Holdout Test Set (15%):** {exp_b_res['split_counts']['holdout_test']:,} samples (evaluated strictly on winner)",
        "",
        "---",
        "",
        "## 3. Experiment A: Binary Classification Benchmarks",
        "",
        "### Candidate Model Comparison on Validation Set (Model Selection Phase)",
        "| Candidate Model | Val Macro F1 | Val Weighted F1 | Val Accuracy | Val Negative F1 | Val Positive F1 | Selection Status |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for model_name, bench in exp_a_res["candidate_benchmarks"].items():
        vm = bench["validation_metrics"]
        neg_f1 = vm["per_class"].get("negative", {}).get("f1_score", 0.0)
        pos_f1 = vm["per_class"].get("positive", {}).get("f1_score", 0.0)
        status = "**Selected Winner**" if model_name == exp_a_res["best_model_name"] else "Baseline / Candidate"
        lines.append(
            f"| **{model_name}** | **{vm['macro_f1']:.4f}** | {vm['weighted_f1']:.4f} | {vm['accuracy']:.4f} | {neg_f1:.4f} | {pos_f1:.4f} | {status} |"
        )

    htm_a = exp_a_res["holdout_test_metrics"]
    lines.extend([
        "",
        f"### Final Independent Holdout Evaluation (Winning Model: `{exp_a_res['best_model_name']}`)",
        f"* **Holdout Accuracy:** {htm_a['accuracy']:.4f} ({htm_a['accuracy'] * 100:.2f}%)",
        f"* **Holdout Macro F1:** {htm_a['macro_f1']:.4f}",
        f"* **Holdout Weighted F1:** {htm_a['weighted_f1']:.4f}",
        f"* **Negative Class:** Precision: {htm_a['per_class']['negative']['precision']:.4f} | Recall: {htm_a['per_class']['negative']['recall']:.4f} | F1: {htm_a['per_class']['negative']['f1_score']:.4f} (Support: {htm_a['per_class']['negative']['support']})",
        f"* **Positive Class:** Precision: {htm_a['per_class']['positive']['precision']:.4f} | Recall: {htm_a['per_class']['positive']['recall']:.4f} | F1: {htm_a['per_class']['positive']['f1_score']:.4f} (Support: {htm_a['per_class']['positive']['support']})",
        "",
        "---",
        "",
        "## 4. Experiment B: Three-Class Classification Benchmarks",
        "",
        "### Candidate Model Comparison on Validation Set (Model Selection Phase)",
        "| Candidate Model | Val Macro F1 | Val Weighted F1 | Val Accuracy | Val Negative F1 | Val Neutral F1 | Val Positive F1 | Selection Status |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])

    for model_name, bench in exp_b_res["candidate_benchmarks"].items():
        vm = bench["validation_metrics"]
        neg_f1 = vm["per_class"].get("negative", {}).get("f1_score", 0.0)
        neu_f1 = vm["per_class"].get("neutral", {}).get("f1_score", 0.0)
        pos_f1 = vm["per_class"].get("positive", {}).get("f1_score", 0.0)
        status = "**Selected Winner**" if model_name == exp_b_res["best_model_name"] else "Baseline / Candidate"
        lines.append(
            f"| **{model_name}** | **{vm['macro_f1']:.4f}** | {vm['weighted_f1']:.4f} | {vm['accuracy']:.4f} | {neg_f1:.4f} | {neu_f1:.4f} | {pos_f1:.4f} | {status} |"
        )

    htm_b = exp_b_res["holdout_test_metrics"]
    lines.extend([
        "",
        f"### Final Independent Holdout Evaluation (Winning Model: `{exp_b_res['best_model_name']}`)",
        f"* **Holdout Accuracy:** {htm_b['accuracy']:.4f} ({htm_b['accuracy'] * 100:.2f}%)",
        f"* **Holdout Macro F1:** {htm_b['macro_f1']:.4f}",
        f"* **Holdout Weighted F1:** {htm_b['weighted_f1']:.4f}",
        f"* **Negative Class:** Precision: {htm_b['per_class']['negative']['precision']:.4f} | Recall: {htm_b['per_class']['negative']['recall']:.4f} | F1: {htm_b['per_class']['negative']['f1_score']:.4f} (Support: {htm_b['per_class']['negative']['support']})",
        f"* **Neutral Class:**  Precision: {htm_b['per_class']['neutral']['precision']:.4f} | Recall: {htm_b['per_class']['neutral']['recall']:.4f} | F1: {htm_b['per_class']['neutral']['f1_score']:.4f} (Support: {htm_b['per_class']['neutral']['support']})",
        f"* **Positive Class:** Precision: {htm_b['per_class']['positive']['precision']:.4f} | Recall: {htm_b['per_class']['positive']['recall']:.4f} | F1: {htm_b['per_class']['positive']['f1_score']:.4f} (Support: {htm_b['per_class']['positive']['support']})",
        "",
        "---",
        "",
        "## 5. Slice-Based Error Analysis on Holdout (ml-best-practices)",
        "",
        "Evaluated on the independent test holdout using the winning three-class model:",
        "",
        "### A. Verified vs. Unverified Purchases",
        "| Customer Cohort | Sample Size | Macro F1 | Accuracy | Negative F1 | Neutral F1 | Positive F1 |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])

    for slice_name, metrics in exp_b_res["slice_analysis"]["verified_purchase"].items():
        pc = metrics["per_class"]
        lines.append(
            f"| **{slice_name}** | {metrics['sample_size']} | {metrics['macro_f1']:.4f} | {metrics['accuracy']:.4f} | {pc.get('negative', {}).get('f1_score', 0.0):.4f} | {pc.get('neutral', {}).get('f1_score', 0.0):.4f} | {pc.get('positive', {}).get('f1_score', 0.0):.4f} |"
        )

    lines.extend([
        "",
        "### B. Short (<30 words) vs. Long (>=30 words) Reviews",
        "| Length Cohort | Sample Size | Macro F1 | Accuracy | Negative F1 | Neutral F1 | Positive F1 |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])

    for slice_name, metrics in exp_b_res["slice_analysis"]["review_length"].items():
        pc = metrics["per_class"]
        lines.append(
            f"| **{slice_name}** | {metrics['sample_size']} | {metrics['macro_f1']:.4f} | {metrics['accuracy']:.4f} | {pc.get('negative', {}).get('f1_score', 0.0):.4f} | {pc.get('neutral', {}).get('f1_score', 0.0):.4f} | {pc.get('positive', {}).get('f1_score', 0.0):.4f} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 6. Persisted Artifacts & Locations",
        "",
        "* **Experiment A (Binary):** `models/experiment_a_binary/`",
        "  - `model.joblib`: Trained standalone classifier",
        "  - `vectorizer.joblib`: Fitted TF-IDF vectorizer",
        "  - `pipeline.joblib`: End-to-end Scikit-learn Pipeline",
        "  - `metrics.json`: JSON performance metrics",
        "  - `confusion_matrix.png`: High-resolution confusion matrix heatmap",
        "* **Experiment B (Three-Class):** `models/experiment_b_3class/`",
        "  - `model.joblib`: Trained standalone classifier",
        "  - `vectorizer.joblib`: Fitted TF-IDF vectorizer",
        "  - `pipeline.joblib`: End-to-end Scikit-learn Pipeline",
        "  - `metrics.json`: JSON performance metrics",
        "  - `confusion_matrix.png`: High-resolution confusion matrix heatmap",
        "* **Cross-Experiment Summary:** `models/experiment_comparison_summary.json`",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    logger.info("Generated markdown evaluation report at %s", output_path)
    return output_path


def run_all_experiments() -> dict:
    """Run Experiment A and Experiment B under strict protocol, save all artifacts, and generate report."""
    start_time = time.time()
    logger.info("Loading Level 4 processed reviews dataset from %s...", FEATURE_COL)
    raw_df = load_processed_reviews()

    # ----------------------------------------------------
    # EXPERIMENT A: BINARY CLASSIFICATION
    # ----------------------------------------------------
    exp_a_df = prepare_dataset(raw_df, experiment_type="binary")
    train_a, val_a, test_a = split_dataset(exp_a_df, target_col="target", random_state=SPLIT_RANDOM_STATE)
    exp_a_results = train_and_benchmark(
        train_df=train_a,
        val_df=val_a,
        test_df=test_a,
        class_names=BINARY_CLASSES,
        experiment_name="Experiment A: Binary Classification",
        text_col=FEATURE_COL,
    )

    save_experiment_artifacts(
        output_dir=EXP_A_DIR,
        model=exp_a_results["best_model"],
        vectorizer=exp_a_results["vectorizer"],
        metrics=exp_a_results,
        class_names=BINARY_CLASSES,
        experiment_title="Experiment A (Binary)",
    )

    # ----------------------------------------------------
    # EXPERIMENT B: THREE-CLASS CLASSIFICATION
    # ----------------------------------------------------
    exp_b_df = prepare_dataset(raw_df, experiment_type="three_class")
    train_b, val_b, test_b = split_dataset(exp_b_df, target_col="target", random_state=SPLIT_RANDOM_STATE)
    exp_b_results = train_and_benchmark(
        train_df=train_b,
        val_df=val_b,
        test_df=test_b,
        class_names=THREE_CLASSES,
        experiment_name="Experiment B: Three-Class Classification",
        text_col=FEATURE_COL,
    )

    save_experiment_artifacts(
        output_dir=EXP_B_DIR,
        model=exp_b_results["best_model"],
        vectorizer=exp_b_results["vectorizer"],
        metrics=exp_b_results,
        class_names=THREE_CLASSES,
        experiment_title="Experiment B (Three-Class)",
    )

    # Cross-experiment summary
    summary = {
        "execution_duration_seconds": round(time.time() - start_time, 2),
        "protocol": {
            "feature_used": FEATURE_COL,
            "prohibited_features_excluded": [
                "cleaned_review_title", "review_title", "star_rating", "rating_category", "review_id", "product_id"
            ],
            "split_random_state": SPLIT_RANDOM_STATE,
            "evaluation_protocol": "Model comparison on Validation set; single evaluation of winner on Holdout test set",
        },
        "experiment_a_binary": {
            "total_samples": len(exp_a_df),
            "split_counts": exp_a_results["split_counts"],
            "best_model": exp_a_results["best_model_name"],
            "validation_macro_f1": exp_a_results["validation_macro_f1"],
            "holdout_test_macro_f1": exp_a_results["holdout_test_metrics"]["macro_f1"],
            "holdout_test_accuracy": exp_a_results["holdout_test_metrics"]["accuracy"],
        },
        "experiment_b_three_class": {
            "total_samples": len(exp_b_df),
            "split_counts": exp_b_results["split_counts"],
            "best_model": exp_b_results["best_model_name"],
            "validation_macro_f1": exp_b_results["validation_macro_f1"],
            "holdout_test_macro_f1": exp_b_results["holdout_test_metrics"]["macro_f1"],
            "holdout_test_accuracy": exp_b_results["holdout_test_metrics"]["accuracy"],
        },
    }

    summary_path = MODELS_DIR / "experiment_comparison_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    logger.info("Saved experiment comparison summary to %s", summary_path)

    report_path = REPORTS_DIR / "sentiment_model_evaluation_report.md"
    generate_markdown_report(exp_a_results, exp_b_results, report_path)

    logger.info("================================================================================")
    logger.info("LEVEL 5 SENTIMENT ANALYSIS EXPERIMENTS COMPLETED (%.2fs)", time.time() - start_time)
    logger.info("================================================================================")
    return summary


if __name__ == "__main__":
    run_all_experiments()
