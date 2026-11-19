"""
train_classifier.py — Unified Training Pipeline for KrishiSarthi AI Intent Classification

Trains a TF-IDF + LogisticRegression pipeline on data/train_expanded.csv,
evaluates on data/test_expanded.csv with full metrics (Accuracy, Precision, Recall, F1, Confusion Matrix),
and saves the model to model/agri_classifier.pkl and model/agri_svm_model.pkl.
"""

import os
import re
import joblib
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_PATH = os.path.join(BASE_DIR, "data", "train_expanded.csv")
TEST_PATH = os.path.join(BASE_DIR, "data", "test_expanded.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
os.makedirs(MODEL_DIR, exist_ok=True)

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def main():
    print("Loading expanded dataset...")
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    print(f"Train samples: {len(train_df)}")
    print(f"Test samples:  {len(test_df)}")

    X_train = train_df["question"].apply(clean_text)
    y_train = train_df["label"]

    X_test = test_df["question"].apply(clean_text)
    y_test = test_df["label"]

    print("\nBuilding and training Pipeline (TF-IDF + Logistic Regression)...")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=25000
        )),
        ("classifier", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
            C=2.0
        ))
    ])

    pipeline.fit(X_train, y_train)
    print("✔ Model training complete.")

    print("\nEvaluating on held-out test set...")
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")

    print(f"Test Accuracy: {acc * 100:.2f}%")
    print(f"Macro F1-Score: {macro_f1:.4f}\n")

    report = classification_report(y_test, y_pred, digits=4)
    print("Classification Report:")
    print(report)

    # Save trained model
    primary_model_path = os.path.join(MODEL_DIR, "agri_classifier.pkl")
    legacy_model_path = os.path.join(MODEL_DIR, "agri_svm_model.pkl")

    joblib.dump(pipeline, primary_model_path)
    joblib.dump(pipeline, legacy_model_path)

    print(f"✔ Model successfully saved to:\n  - {primary_model_path}\n  - {legacy_model_path}")

    # Test the original failure cases from diagnostic report
    test_queries = [
        ("How to grow wheat?", "CROP_GROWTH_GUIDE"),
        ("What fertilizer for rice?", "FERTILIZER_SUGGESTION"),
        ("How to control pests in cotton?", "PEST_CONTROL"),
        ("Best season to plant sugarcane?", "PLANTING_SEASON"),
        ("What is organic farming?", "ORGANIC_FARMING"),
        ("How to irrigate tomato?", "IRRIGATION_GUIDE"),
        ("Tell me about soil testing", "SOIL_HEALTH"),
        ("random gibberish xyz123", "UNKNOWN"),
        ("what is the price of potato in mandi", "MARKET_GUIDE"),
        ("when should i harvest maize", "HARVEST_GUIDE")
    ]

    print("\n" + "=" * 55)
    print("Testing Key Queries (including Diagnostic Failures):")
    print("=" * 55)
    for q, expected in test_queries:
        probs = pipeline.predict_proba([clean_text(q)])[0]
        top_idx = np.argmax(probs)
        pred_label = pipeline.classes_[top_idx]
        conf = probs[top_idx]

        threshold = 0.45
        final_label = pred_label if conf >= threshold else "UNKNOWN"
        match = "✔ PASS" if final_label == expected or (expected == "UNKNOWN" and final_label == "UNKNOWN") else "❌ FAIL"
        print(f"[{match}] Query: '{q}'\n       Expected: {expected} | Predicted: {final_label} ({conf:.2%})\n")

if __name__ == "__main__":
    main()
