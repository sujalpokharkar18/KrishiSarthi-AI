# api/timetable_engine.py
"""
Timetable generation engine: Combines crop growth stages with weather conditions
to generate an actionable day-by-day timetable for farmers.
"""

from datetime import datetime, timedelta
from dataset_loader import get_crop_rules, normalize_crop_name


def generate_timetable(crop: str, start_date: str, weather: list):
    """
    Generate a weather-aware farming timetable for the given crop.

    Parameters:
        crop: Crop name (e.g. 'Wheat', 'Tomato', 'gehu')
        start_date: Start date in 'YYYY-MM-DD' format
        weather: List of daily weather dicts, e.g.
                 [{"condition": "Sunny", "rain_mm": 0, "temp_c": 28}, ...]

    Returns:
        List of dicts: [{"day": 1, "date": "2026-09-03", "task": "..."}, ...]
    """
    rules = get_crop_rules(crop)
    if not rules:
        return None

    # Parse and validate start date
    try:
        date_obj = datetime.strptime(start_date.strip(), "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid start_date '{start_date}'. Expected format: YYYY-MM-DD (e.g. 2026-09-03)")

    normal_tasks = rules.get("normal", [])
    rain_tasks = rules.get("rain", [])
    hot_tasks = rules.get("hot", [])
    cold_tasks = rules.get("cold", [])

    if not normal_tasks:
        normal_tasks = ["Perform regular field inspection and maintenance"]

    timetable = []

    for i, day_data in enumerate(weather):
        if not isinstance(day_data, dict):
            continue

        condition = str(day_data.get("condition", "")).lower()
        try:
            rain_mm = float(day_data.get("rain_mm", 0) or 0)
        except (ValueError, TypeError):
            rain_mm = 0.0

        try:
            temp_c = float(day_data.get("temp_c", 0) or 0) if day_data.get("temp_c") is not None else None
        except (ValueError, TypeError):
            temp_c = None

        # ──────── Weather Decision Logic ────────
        # 1. Rain condition
        if "rain" in condition or rain_mm > 10.0:
            task = rain_tasks[min(i, len(rain_tasks) - 1)]

        # 2. Hot weather condition
        elif "hot" in condition or (temp_c is not None and temp_c > 32.0):
            task = hot_tasks[min(i, len(hot_tasks) - 1)]

        # 3. Cold weather condition
        elif "cold" in condition or (temp_c is not None and temp_c < 15.0):
            task = cold_tasks[min(i, len(cold_tasks) - 1)]

        # 4. Default normal growth stage task
        else:
            task = normal_tasks[min(i, len(normal_tasks) - 1)]

        day_date_str = (date_obj + timedelta(days=i)).strftime("%Y-%m-%d")

        timetable.append({
            "day": i + 1,
            "date": day_date_str,
            "task": task
        })

    return timetable
