"""
ai_engine.py — KrishiSarthi AI Question-Answering Engine

Loads the trained classification model and provides intent prediction
with confidence thresholding and unknown-question handling.
"""

import joblib
import json
import numpy as np
import os
import re

# ─── File Paths ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "agri_classifier.pkl")
RESPONSES_PATH = os.path.join(BASE_DIR, "api", "responses.json")

# ─── Confidence Threshold ────────────────────────────────────
# Questions below this confidence are classified as UNKNOWN.
# Tuned on validation data — adjust if precision/recall trade-off changes.
CONFIDENCE_THRESHOLD = 0.45

# ─── Load Model (sklearn Pipeline: TfidfVectorizer + LogisticRegression) ──
try:
    model = joblib.load(MODEL_PATH)
    print(f"[OK] AI model loaded from {MODEL_PATH}")
except FileNotFoundError:
    # Fallback to old model path for backward compatibility
    OLD_MODEL_PATH = os.path.join(BASE_DIR, "model", "agri_svm_model.pkl")
    model = joblib.load(OLD_MODEL_PATH)
    print(f"[WARN] Loaded fallback model from {OLD_MODEL_PATH}")

# ─── Load Response Templates ─────────────────────────────────
with open(RESPONSES_PATH, "r", encoding="utf-8") as f:
    responses = json.load(f)


def clean_text(text: str) -> str:
    """Basic text cleaning: lowercase, strip, remove special chars."""
    text = text.lower().strip()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def predict_label(question: str):
    """
    Predicts the intent label and confidence from the user's question.

    Returns:
        (label, confidence) — If confidence < CONFIDENCE_THRESHOLD,
        returns ("UNKNOWN", confidence) instead.
    """
    cleaned = clean_text(question)

    if not cleaned:
        return "UNKNOWN", 0.0

    # Get probabilities from the model
    probabilities = model.predict_proba([cleaned])[0]

    # Highest probability index
    index = np.argmax(probabilities)

    # Final output
    label = model.classes_[index]
    confidence = float(probabilities[index])

    # Apply confidence threshold
    if confidence < CONFIDENCE_THRESHOLD:
        return "UNKNOWN", confidence

    return label, confidence


def get_response_for_label(label: str) -> str:
    """
    Returns the AI reply text from responses.json for the given label.
    Falls back to the UNKNOWN response if the label is not found.
    """
    unknown_reply = responses.get(
        "UNKNOWN",
        "I'm sorry, I couldn't understand your question. "
        "Please ask a farming-related question."
    )
    return responses.get(label, unknown_reply)
