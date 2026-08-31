from pathlib import Path

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


# ============================================
# PATHS
# ============================================

BASE_DIR = Path(__file__).resolve().parent

RESULTS_DIR = BASE_DIR / "results"

PREDICTIONS_FILE = (
    RESULTS_DIR
    / "ai_predictions_1000.csv"
)


# ============================================
# LOAD RESULTS
# ============================================

print("=" * 50)
print("AI MODERATION PERFORMANCE EVALUATION")
print("=" * 50)


if not PREDICTIONS_FILE.exists():
    raise FileNotFoundError(
        f"\nPrediction file not found:\n"
        f"{PREDICTIONS_FILE}\n\n"
        "Run evaluate_ai.py first."
    )


df = pd.read_csv(
    PREDICTIONS_FILE
)


print(
    f"\nPredictions loaded: {len(df)}"
)


# ============================================
# CHECK REQUIRED COLUMNS
# ============================================

required_columns = [
    "actual_harmful",
    "predicted_harmful",
]


for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Required column missing: {column}"
        )


# Remove incomplete rows if any exist.

df = df.dropna(
    subset=required_columns
)


df["actual_harmful"] = (
    df["actual_harmful"]
    .astype(int)
)


df["predicted_harmful"] = (
    df["predicted_harmful"]
    .astype(int)
)


# ============================================
# ACTUAL AND PREDICTED LABELS
# ============================================

y_true = df[
    "actual_harmful"
]

y_pred = df[
    "predicted_harmful"
]


# ============================================
# BASIC METRICS
# ============================================

accuracy = accuracy_score(
    y_true,
    y_pred,
)


precision = precision_score(
    y_true,
    y_pred,
    zero_division=0,
)


recall = recall_score(
    y_true,
    y_pred,
    zero_division=0,
)


f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0,
)


# ============================================
# CONFUSION MATRIX
# ============================================

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1],
)


tn, fp, fn, tp = cm.ravel()


# ============================================
# FALSE POSITIVE / NEGATIVE RATES
# ============================================

false_positive_rate = (
    fp / (fp + tn)
    if (fp + tn) > 0
    else 0
)


false_negative_rate = (
    fn / (fn + tp)
    if (fn + tp) > 0
    else 0
)


# ============================================
# DISPLAY RESULTS
# ============================================

print("\n")
print("=" * 50)
print("PERFORMANCE METRICS")
print("=" * 50)


print(
    f"Accuracy:  {accuracy:.4f} "
    f"({accuracy * 100:.2f}%)"
)


print(
    f"Precision: {precision:.4f} "
    f"({precision * 100:.2f}%)"
)


print(
    f"Recall:    {recall:.4f} "
    f"({recall * 100:.2f}%)"
)


print(
    f"F1-score:  {f1:.4f} "
    f"({f1 * 100:.2f}%)"
)


print("\n")
print("=" * 50)
print("CONFUSION MATRIX")
print("=" * 50)


print(
    f"True Negatives  (TN): {tn}"
)

print(
    f"False Positives (FP): {fp}"
)

print(
    f"False Negatives (FN): {fn}"
)

print(
    f"True Positives  (TP): {tp}"
)


print(
    "\nFalse Positive Rate: "
    f"{false_positive_rate:.4f} "
    f"({false_positive_rate * 100:.2f}%)"
)


print(
    "False Negative Rate: "
    f"{false_negative_rate:.4f} "
    f"({false_negative_rate * 100:.2f}%)"
)


# ============================================
# CLASSIFICATION REPORT
# ============================================

print("\n")
print("=" * 50)
print("CLASSIFICATION REPORT")
print("=" * 50)


report_text = classification_report(
    y_true,
    y_pred,
    labels=[0, 1],
    target_names=[
        "Safe",
        "Harmful",
    ],
    zero_division=0,
)


print(
    report_text
)


# ============================================
# SAVE METRICS
# ============================================

metrics_df = pd.DataFrame(
    {
        "Metric": [
            "Accuracy",
            "Precision",
            "Recall",
            "F1-score",
            "True Positives",
            "True Negatives",
            "False Positives",
            "False Negatives",
            "False Positive Rate",
            "False Negative Rate",
        ],

        "Value": [
            accuracy,
            precision,
            recall,
            f1,
            int(tp),
            int(tn),
            int(fp),
            int(fn),
            false_positive_rate,
            false_negative_rate,
        ],
    }
)


metrics_file = (
    RESULTS_DIR
    / "ai_metrics.csv"
)


metrics_df.to_csv(
    metrics_file,
    index=False,
)


# ============================================
# SAVE CLASSIFICATION REPORT
# ============================================

report_file = (
    RESULTS_DIR
    / "classification_report.txt"
)


with open(
    report_file,
    "w",
    encoding="utf-8",
) as file:

    file.write(
        "AI MODERATION CLASSIFICATION REPORT\n"
    )

    file.write(
        "=" * 50
    )

    file.write(
        "\n\n"
    )

    file.write(
        report_text
    )


print("\n")
print("=" * 50)
print("FILES SAVED")
print("=" * 50)


print(
    f"\nMetrics:\n{metrics_file}"
)


print(
    f"\nClassification report:\n"
    f"{report_file}"
)