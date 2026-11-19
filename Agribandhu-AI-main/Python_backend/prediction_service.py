"""
prediction_service.py — Random Forest Prediction Service for KrishiSarthi AI

Loads the trained Random Forest model and predicts daily agricultural actions
based on current weather parameters and crop stage.
"""

import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATHS = [
    os.path.join(BASE_DIR, "model", "agribandhu_rf_model.pkl"),
    os.path.join(BASE_DIR, "agribandhu_rf_model.pkl")
]

_rf_model = None

ACTIONS = {
    0: "Sowing",
    1: "Irrigation",
    2: "Fertilizer",
    3: "Pesticide",
    4: "Wait",
    5: "Harvest"
}

STAGES = {
    0: "Seedling",
    1: "Vegetative Growth",
    2: "Flowering",
    3: "Harvest Ready"
}


def get_rf_model():
    global _rf_model
    if _rf_model is None:
        for path in MODEL_PATHS:
            if os.path.exists(path):
                _rf_model = joblib.load(path)
                break
        if _rf_model is None:
            raise FileNotFoundError("Could not find agribandhu_rf_model.pkl")
    return _rf_model


def get_next_stage(current_stage: int, action: str) -> int:
    """Calculates progression to next biological stage based on completed farming action."""
    if current_stage == 0 and action in ("Sowing", "Irrigation"):
        return 1
    elif current_stage == 1 and action in ("Fertilizer", "Pesticide"):
        return 2
    elif current_stage == 2 and action in ("Fertilizer", "Harvest"):
        return 3
    return current_stage


def predict_action(temp: float, humidity: float, rain: float, wind: float, crop_stage: int, date: str):
    """
    Predicts the recommended action for a crop on a specific date.

    Returns:
        dict with date, action, currentStage, nextStage, stageChanged, explanation
    """
    model = get_rf_model()

    # Create feature dataframe
    features = pd.DataFrame(
        [[float(temp), float(humidity), float(rain), float(wind), int(crop_stage)]],
        columns=["temp", "humidity", "rain", "wind", "crop_stage"]
    )

    pred_class = int(model.predict(features)[0])
    action = ACTIONS.get(pred_class, "Wait")
    next_stage = get_next_stage(crop_stage, action)

    if action == "Wait":
        explanation = "Weather conditions or crop stage do not require immediate intervention today."
    elif action == "Irrigation":
        explanation = f"Moisture deficit detected ({temp}°C, {humidity}% humidity). Irrigation recommended."
    elif action == "Fertilizer":
        explanation = f"Favorable conditions for nutrient uptake at {STAGES.get(crop_stage, 'current')} stage."
    elif action == "Pesticide":
        explanation = f"High humidity ({humidity}%) increases disease risk. Preventive spray recommended."
    elif action == "Harvest":
        explanation = "Dry weather conditions are ideal for harvesting mature crop."
    else:
        explanation = f"{action} is recommended based on weather and stage analysis."

    return {
        "date": str(date),
        "action": action,
        "currentStage": STAGES.get(crop_stage, "Unknown"),
        "nextStage": STAGES.get(next_stage, "Unknown"),
        "stageChanged": next_stage != crop_stage,
        "explanation": explanation
    }
