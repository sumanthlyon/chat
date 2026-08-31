import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()


HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN is missing from the .env file"
    )


client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)


MODEL_NAME = "unitary/toxic-bert"


TOXIC_LABELS = {
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate",
}


WARNING_THRESHOLD = 0.70


def analyse_message(text: str):
    if not text or not text.strip():
        return {
            "label": "UNKNOWN",
            "score": 0.0,
            "warning": False,
            "message": "No text was provided for analysis",
        }

    cleaned_text = text.strip()

    result = client.text_classification(
        cleaned_text,
        model=MODEL_NAME,
    )

    if not result:
        return {
            "label": "UNKNOWN",
            "score": 0.0,
            "warning": False,
            "message": "No AI classification result was returned",
        }

    print("AI RESULT:", result)

    best_result = max(
        result,
        key=lambda item: item.score,
    )

    label = str(
        best_result.label
    )

    score = float(
        best_result.score
    )

    normalized_label = (
        label
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

    warning = (
        normalized_label in TOXIC_LABELS
        and score >= WARNING_THRESHOLD
    )

    if warning:
        result_message = (
            "Potentially harmful language detected"
        )
    else:
        result_message = (
            "No strong harmful-language signal detected"
        )

    return {
        "label": label,
        "score": score,
        "warning": warning,
        "message": result_message,
    }