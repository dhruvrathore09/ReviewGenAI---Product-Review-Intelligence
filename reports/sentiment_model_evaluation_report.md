# Level 5: Sentiment Analysis Model Evaluation Report

**Project:** Product Review Intelligence Platform  
**Milestone:** Level 5 — Sentiment Analysis using Machine Learning  
**Protocol:** Strict Dataset Contract Compliance & Sealed Holdout Evaluation  
**Input Feature:** `cleaned_review_text` STRICTLY (titles & metadata excluded)  
**Fresh Holdout Random Seed:** `2026`  

---

## 1. Executive Summary & Experimental Protocol

Level 5 evaluates machine learning models on customer reviews from the Amazon Reviews 2023 Electronics dataset under a strict experimental protocol:

1. **Input Feature Isolation**: Models are trained **strictly on `cleaned_review_text`**. Review titles, IDs, product metadata, and numerical ratings are strictly excluded from TF-IDF feature extraction to guarantee zero target leakage.
2. **Strict Model Selection Protocol**: Candidate models are trained on the Training set and compared **strictly on the Validation set** using **Validation Macro F1**. The test holdout is never touched during model comparison.
3. **Independent Holdout Evaluation**: A fresh, sealed holdout test set (15%) is established and evaluated **strictly on the single selected winning model** once selection is final.
4. **Weak-Supervision Proxy Labels**: Target labels are derived directly from customer `star_rating` as heuristic proxy labels (1-2: negative, 3: neutral, 4-5: positive).

---

## 2. Dataset Split Distributions

In compliance with `ml-best-practices`, **Strict Featurization Ordering** was enforced: datasets were split into stratified Train (70%), Validation (15%), and Holdout Test (15%) splits **before** TF-IDF vocabulary fitting.

### Experiment A (Binary) Split Counts (3-Star Reviews Excluded)
- **Total Reviews:** 7,466
- **Train Set (70%):** 5,226 samples
- **Validation Set (15%):** 1,120 samples (used for candidate comparison)
- **Holdout Test Set (15%):** 1,120 samples (evaluated strictly on winner)

### Experiment B (Three-Class) Split Counts (All Reviews Included)
- **Total Reviews:** 7,991
- **Train Set (70%):** 5,593 samples
- **Validation Set (15%):** 1,199 samples (used for candidate comparison)
- **Holdout Test Set (15%):** 1,199 samples (evaluated strictly on winner)

---

## 3. Experiment A: Binary Classification Benchmarks

### Candidate Model Comparison on Validation Set (Model Selection Phase)
| Candidate Model | Val Macro F1 | Val Weighted F1 | Val Accuracy | Val Negative F1 | Val Positive F1 | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dummy Baseline** | **0.4669** | 0.8179 | 0.8759 | 0.0000 | 0.9338 | Baseline / Candidate |
| **Multinomial Naive Bayes** | **0.5797** | 0.8517 | 0.8911 | 0.2179 | 0.9415 | Baseline / Candidate |
| **Logistic Regression (Balanced)** | **0.8203** | 0.9180 | 0.9143 | 0.6903 | 0.9503 | Baseline / Candidate |
| **Calibrated Linear SVM** | **0.8210** | 0.9266 | 0.9313 | 0.6805 | 0.9615 | **Selected Winner** |

### Final Independent Holdout Evaluation (Winning Model: `Calibrated Linear SVM`)
* **Holdout Accuracy:** 0.9232 (92.32%)
* **Holdout Macro F1:** 0.8008
* **Holdout Weighted F1:** 0.9179
* **Negative Class:** Precision: 0.7647 | Recall: 0.5571 | F1: 0.6446 (Support: 140)
* **Positive Class:** Precision: 0.9391 | Recall: 0.9755 | F1: 0.9570 (Support: 980)

---

## 4. Experiment B: Three-Class Classification Benchmarks

### Candidate Model Comparison on Validation Set (Model Selection Phase)
| Candidate Model | Val Macro F1 | Val Weighted F1 | Val Accuracy | Val Negative F1 | Val Neutral F1 | Val Positive F1 | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dummy Baseline** | **0.3000** | 0.7364 | 0.8182 | 0.0000 | 0.0000 | 0.9000 | Baseline / Candidate |
| **Multinomial Naive Bayes** | **0.3625** | 0.7624 | 0.8299 | 0.1818 | 0.0000 | 0.9058 | Baseline / Candidate |
| **Logistic Regression (Balanced)** | **0.5943** | 0.8304 | 0.8182 | 0.5704 | 0.3030 | 0.9094 | **Selected Winner** |
| **Calibrated Linear SVM** | **0.5361** | 0.8390 | 0.8691 | 0.6076 | 0.0674 | 0.9334 | Baseline / Candidate |

### Final Independent Holdout Evaluation (Winning Model: `Logistic Regression (Balanced)`)
* **Holdout Accuracy:** 0.8232 (82.32%)
* **Holdout Macro F1:** 0.6114
* **Holdout Weighted F1:** 0.8359
* **Negative Class:** Precision: 0.5371 | Recall: 0.6763 | F1: 0.5987 (Support: 139)
* **Neutral Class:**  Precision: 0.2768 | Recall: 0.3924 | F1: 0.3246 (Support: 79)
* **Positive Class:** Precision: 0.9452 | Recall: 0.8787 | F1: 0.9107 (Support: 981)

---

## 5. Slice-Based Error Analysis on Holdout (ml-best-practices)

Evaluated on the independent test holdout using the winning three-class model:

### A. Verified vs. Unverified Purchases
| Customer Cohort | Sample Size | Macro F1 | Accuracy | Negative F1 | Neutral F1 | Positive F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Unverified Purchase** | 280 | 0.5377 | 0.8214 | 0.4545 | 0.2400 | 0.9185 |
| **Verified Purchase** | 919 | 0.6283 | 0.8237 | 0.6222 | 0.3546 | 0.9082 |

### B. Short (<30 words) vs. Long (>=30 words) Reviews
| Length Cohort | Sample Size | Macro F1 | Accuracy | Negative F1 | Neutral F1 | Positive F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Long (>=30 words)** | 682 | 0.5786 | 0.7727 | 0.5083 | 0.3467 | 0.8809 |
| **Short (<30 words)** | 517 | 0.6374 | 0.8897 | 0.7218 | 0.2439 | 0.9465 |

---

## 6. Persisted Artifacts & Locations

* **Experiment A (Binary):** `models/experiment_a_binary/`
  - `model.joblib`: Trained standalone classifier
  - `vectorizer.joblib`: Fitted TF-IDF vectorizer
  - `pipeline.joblib`: End-to-end Scikit-learn Pipeline
  - `metrics.json`: JSON performance metrics
  - `confusion_matrix.png`: High-resolution confusion matrix heatmap
* **Experiment B (Three-Class):** `models/experiment_b_3class/`
  - `model.joblib`: Trained standalone classifier
  - `vectorizer.joblib`: Fitted TF-IDF vectorizer
  - `pipeline.joblib`: End-to-end Scikit-learn Pipeline
  - `metrics.json`: JSON performance metrics
  - `confusion_matrix.png`: High-resolution confusion matrix heatmap
* **Cross-Experiment Summary:** `models/experiment_comparison_summary.json`
