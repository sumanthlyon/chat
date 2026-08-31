from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.metrics import confusion_matrix


# ============================================
# PATHS
# ============================================

BASE_DIR = Path(__file__).resolve().parent

RESULTS_DIR = BASE_DIR / "results"

PREDICTIONS_FILE = (
    RESULTS_DIR
    / "ai_predictions.csv"
)


# ============================================
# CHECK FILE
# ============================================

if not PREDICTIONS_FILE.exists():
    raise FileNotFoundError(
        f"Prediction file not found:\n"
        f"{PREDICTIONS_FILE}\n\n"
        "Run evaluate_ai.py first."
    )


# ============================================
# LOAD PREDICTIONS
# ============================================

df = pd.read_csv(
    PREDICTIONS_FILE
)


print("=" * 60)
print("AI MODERATION ERROR ANALYSIS")
print("=" * 60)

print(
    f"\nTotal predictions: {len(df)}"
)


# ============================================
# REMOVE INCOMPLETE ROWS
# ============================================

df = df.dropna(
    subset=[
        "actual_harmful",
        "predicted_harmful",
    ]
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
# FIND TRUE POSITIVES
# ============================================

true_positives = df[
    (df["actual_harmful"] == 1)
    &
    (df["predicted_harmful"] == 1)
]


# ============================================
# FIND TRUE NEGATIVES
# ============================================

true_negatives = df[
    (df["actual_harmful"] == 0)
    &
    (df["predicted_harmful"] == 0)
]


# ============================================
# FIND FALSE POSITIVES
# ============================================

false_positives = df[
    (df["actual_harmful"] == 0)
    &
    (df["predicted_harmful"] == 1)
]


# ============================================
# FIND FALSE NEGATIVES
# ============================================

false_negatives = df[
    (df["actual_harmful"] == 1)
    &
    (df["predicted_harmful"] == 0)
]


# ============================================
# DISPLAY COUNTS
# ============================================

print("\nRESULT COUNTS")
print("-" * 40)

print(
    f"True Positives:  {len(true_positives)}"
)

print(
    f"True Negatives:  {len(true_negatives)}"
)

print(
    f"False Positives: {len(false_positives)}"
)

print(
    f"False Negatives: {len(false_negatives)}"
)


# ============================================
# SAVE FALSE POSITIVES
# ============================================

false_positive_file = (
    RESULTS_DIR
    / "false_positives.csv"
)


false_positives.to_csv(
    false_positive_file,
    index=False,
)


# ============================================
# SAVE FALSE NEGATIVES
# ============================================

false_negative_file = (
    RESULTS_DIR
    / "false_negatives.csv"
)


false_negatives.to_csv(
    false_negative_file,
    index=False,
)


# ============================================
# PRINT FALSE NEGATIVES
# ============================================

print("\n")
print("=" * 60)
print("FALSE NEGATIVES")
print("=" * 60)


if len(false_negatives) == 0:

    print(
        "\nNo false negatives found."
    )

else:

    for number, (_, row) in enumerate(
        false_negatives.iterrows(),
        start=1,
    ):

        print(
            f"\nFalse Negative #{number}"
        )

        print("-" * 40)

        print(
            "Comment:"
        )

        print(
            row["comment_text"]
        )

        print(
            "\nAI label:",
            row.get(
                "ai_label",
                "Unknown",
            ),
        )

        print(
            "AI score:",
            row.get(
                "ai_score",
                "Unknown",
            ),
        )


# ============================================
# PRINT FALSE POSITIVES
# ============================================

print("\n")
print("=" * 60)
print("FALSE POSITIVES")
print("=" * 60)


if len(false_positives) == 0:

    print(
        "\nNo false positives found."
    )

else:

    for number, (_, row) in enumerate(
        false_positives.iterrows(),
        start=1,
    ):

        print(
            f"\nFalse Positive #{number}"
        )

        print("-" * 40)

        print(
            row["comment_text"]
        )

        print(
            "\nAI label:",
            row.get(
                "ai_label",
                "Unknown",
            ),
        )

        print(
            "AI score:",
            row.get(
                "ai_score",
                "Unknown",
            ),
        )


# ============================================
# CREATE CONFUSION MATRIX
# ============================================

y_true = df[
    "actual_harmful"
]

y_pred = df[
    "predicted_harmful"
]


cm = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1],
)


# ============================================
# CREATE FIGURE
# ============================================

fig, ax = plt.subplots(
    figsize=(7, 6)
)


image = ax.imshow(
    cm
)


# ============================================
# LABEL AXES
# ============================================

ax.set_xticks(
    [0, 1]
)

ax.set_yticks(
    [0, 1]
)


ax.set_xticklabels(
    [
        "Predicted Safe",
        "Predicted Harmful",
    ]
)


ax.set_yticklabels(
    [
        "Actual Safe",
        "Actual Harmful",
    ]
)


ax.set_xlabel(
    "Predicted Classification"
)


ax.set_ylabel(
    "Actual Classification"
)


ax.set_title(
    "AI Toxicity Detection Confusion Matrix"
)


# ============================================
# ADD NUMBERS TO CELLS
# ============================================

for i in range(
    cm.shape[0]
):

    for j in range(
        cm.shape[1]
    ):

        ax.text(
            j,
            i,
            str(cm[i, j]),
            ha="center",
            va="center",
            fontsize=16,
        )


# ============================================
# ADD COLOUR BAR
# ============================================

fig.colorbar(
    image,
    ax=ax,
)


fig.tight_layout()


# ============================================
# SAVE CONFUSION MATRIX
# ============================================

confusion_matrix_file = (
    RESULTS_DIR
    / "confusion_matrix.png"
)


plt.savefig(
    confusion_matrix_file,
    dpi=300,
    bbox_inches="tight",
)


plt.close()


# ============================================
# FINISHED
# ============================================

print("\n")
print("=" * 60)
print("FILES CREATED")
print("=" * 60)


print(
    "\nFalse positives:"
)

print(
    false_positive_file
)


print(
    "\nFalse negatives:"
)

print(
    false_negative_file
)


print(
    "\nConfusion matrix:"
)

print(
    confusion_matrix_file
)


print(
    "\nError analysis completed successfully."
)