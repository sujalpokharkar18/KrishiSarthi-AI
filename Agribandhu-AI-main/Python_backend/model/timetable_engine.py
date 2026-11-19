"""
model/timetable_engine.py — Timetable Prediction Module

Legacy wrapper: Redirects to the production rule-based timetable engine in the parent directory.
The experimental LSTM service was removed in favor of the deterministic, weather-aware timetable generator.
"""

import os
import sys

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from timetable_engine import generate_timetable as core_generate_timetable


def generate_timetable(recent_data):
    """
    Backward-compatible helper function for legacy scripts.
    Generates recommended task based on days elapsed or weather observations.
    """
    if isinstance(recent_data, (int, float)):
        days = int(recent_data)
    elif isinstance(recent_data, list):
        days = len(recent_data)
    else:
        days = 10

    if days <= 5:
        task = "Irrigation and Soil Moisture Check"
    elif days <= 20:
        task = "Fertilizer Application (NPK)"
    elif days <= 45:
        task = "Pesticide and Weed Management"
    else:
        task = "Harvest Preparation and Crop Drying"

    return {
        "after_days": days,
        "task": task
    }
