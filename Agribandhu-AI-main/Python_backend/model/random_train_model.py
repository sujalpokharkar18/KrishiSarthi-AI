"""
model/random_train_model.py — Training Pipeline for AgriBandhu Random Forest Daily Crop Actions

Generates an agronomically consistent dataset and trains a RandomForestClassifier
for predicting optimal daily actions (Sowing, Irrigation, Fertilizer, Pesticide, Wait, Harvest)
based on weather features (temp, humidity, rain, wind) and crop growth stage.
"""

import os
import random
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)
DATA_FILE = os.path.join(BACKEND_DIR, "data", "agribandhu_training_data.csv")
MODEL_SAVE_PATH_1 = os.path.join(BASE_DIR, "agribandhu_rf_model.pkl")
MODEL_SAVE_PATH_2 = os.path.join(BACKEND_DIR, "agribandhu_rf_model.pkl")

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


def generate_synthetic_agricultural_data(n_samples=2500):
    rows = []
    random.seed(42)
    np.random.seed(42)

    for _ in range(n_samples):
        crop_stage = random.choice([0, 1, 2, 3])
        temp = round(random.uniform(15.0, 42.0), 1)
        humidity = round(random.uniform(25.0, 95.0), 1)
        # Rain probability: 30% rainy days
        rain = round(random.uniform(5.0, 45.0), 1) if random.random() < 0.3 else 0.0
        wind = round(random.uniform(1.0, 25.0), 1)

        # ── Agronomic Decision Logic ──
        # 1. Rain or high wind -> Wait (spraying and irrigation prohibited during storm/rain)
        if rain > 5.0 or wind > 18.0:
            action = 4  # Wait

        # 2. Harvest Ready (Stage 3) -> Harvest if dry and mild wind
        elif crop_stage == 3:
            if rain == 0.0 and humidity < 75.0:
                action = 5  # Harvest
            else:
                action = 4  # Wait for dry weather

        # 3. Seedling (Stage 0) -> Sowing / Light Irrigation
        elif crop_stage == 0:
            if temp < 35.0 and humidity >= 40.0:
                action = 0  # Sowing
            else:
                action = 1  # Irrigation

        # 4. Vegetative Growth (Stage 1) -> Fertilizer or Irrigation
        elif crop_stage == 1:
            if temp > 32.0 or humidity < 40.0:
                action = 1  # Irrigation
            elif 45.0 <= humidity <= 75.0 and temp <= 32.0:
                action = 2  # Fertilizer
            elif humidity > 80.0:
                action = 3  # High humidity pest risk
            else:
                action = 4  # Wait

        # 5. Flowering (Stage 2) -> Pest Control or Fertilizer
        elif crop_stage == 2:
            if humidity > 70.0 or (22.0 <= temp <= 30.0 and humidity > 60.0):
                action = 3  # Pesticide (fungal / insect risk during bloom)
            elif temp > 33.0 or humidity < 35.0:
                action = 1  # Irrigation (protect blossoms)
            elif 40.0 <= humidity <= 65.0:
                action = 2  # Micronutrient / Fertilizer
            else:
                action = 4  # Wait

        else:
            action = 4

        rows.append({
            "temp": temp,
            "humidity": humidity,
            "rain": rain,
            "wind": wind,
            "crop_stage": crop_stage,
            "action": action
        })

    return pd.DataFrame(rows)


def main():
    print("Generating comprehensive agricultural training data...")
    df = generate_synthetic_agricultural_data(3000)
    df.to_csv(DATA_FILE, index=False)
    print(f"✔ Saved dataset with {len(df)} rows to {DATA_FILE}")

    X = df[["temp", "humidity", "rain", "wind", "crop_stage"]]
    y = df["action"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✔ Model Accuracy on test split: {acc * 100:.2f}%")

    # Save to both model/ and backend root so all paths find it
    joblib.dump(model, MODEL_SAVE_PATH_1)
    joblib.dump(model, MODEL_SAVE_PATH_2)
    print(f"✔ Model saved to:\n  - {MODEL_SAVE_PATH_1}\n  - {MODEL_SAVE_PATH_2}")


if __name__ == "__main__":
    main()
