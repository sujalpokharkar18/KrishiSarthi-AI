# AgriBandhu AI — Full Project Diagnostic Report

> **Diagnosed on:** 2026-09-03  
> **Scope:** Python Backend + Android App  
> **Method:** Code review of every file + live API endpoint testing

---

## Executive Summary

| Area | Working | Partially Working | Broken |
|------|:-------:|:-----------------:|:------:|
| Backend API | 2 endpoints | 1 (quality issues) | 0 |
| AI Question Answering | ✅ | ⚠️ (accuracy) | — |
| AI Timetable Generation | ✅ | ⚠️ (quality) | — |
| Android Login/Signup | — | — | 🔴 Insecure |
| Android AI Chat (`/ask`) | — | ⚠️ | — |
| Android AI Timetable | — | — | 🔴 Broken |
| Android Weather Page | — | ⚠️ | — |
| Android Post/Community Feed | — | — | 🔴 Broken |
| Android Schemes Page | — | ⚠️ | — |
| Android Crop Tracking | — | — | 🔴 Broken |
| LSTM Model Pipeline | — | — | 🔴 Missing code |

---

## Part 1: Python Backend Diagnosis

### ✅ WORKING — `GET /` Health Check
- Returns `{"message": "AgriBandhu AI API running"}`
- **Status: PASS**

---

### ⚠️ PARTIALLY WORKING — `POST /ask` (AI Question Answering)

The endpoint **runs without crashing**, but has significant quality and accuracy issues:

| Test Question | Predicted Label | Confidence | Correct? |
|---|---|---|---|
| "How to grow wheat?" | STORAGE_GUIDE | 0.6139 | ❌ Wrong |
| "What fertilizer for rice?" | FERTILIZER_SUGGESTION | 0.8631 | ✅ |
| "How to control pests in cotton?" | STORAGE_GUIDE | 0.4250 | ❌ Wrong |
| "Best season to plant sugarcane?" | FERTILIZER_SUGGESTION | 0.4306 | ❌ Wrong |
| "What is organic farming?" | WEATHER_QUERY | 0.9153 | ❌ Wrong |
| "How to irrigate tomato?" | IRRIGATION_GUIDE | 0.6944 | ✅ |
| "Tell me about soil testing" | SOIL_HEALTH | 0.9220 | ✅ |
| "random gibberish xyz123" | SOIL_HEALTH | 0.4233 | ❌ No "unknown" handling |

#### Issues Found:

1. **Poor model accuracy** — Only 3/7 real questions are classified correctly. The model frequently misclassifies questions (e.g., "How to grow wheat?" → STORAGE_GUIDE).

2. **Only 7 response categories** — `responses.json` only has labels: `CROP_DISEASE`, `FERTILIZER_SUGGESTION`, `IRRIGATION_GUIDE`, `WEATHER_QUERY`, `SOIL_HEALTH`, `STORAGE_GUIDE`, `SEED_GUIDE`. Many important farming topics (pest control, organic farming, crop growth guidance, harvest timing) have **no category at all**.

3. **No "I don't know" fallback** — Random gibberish still returns a confident-looking answer (SOIL_HEALTH at 42% confidence). There's no confidence threshold to say "I don't understand."

4. **sklearn version mismatch warning** — The `.pkl` models were trained with scikit-learn 1.7.2 but loaded with 1.9.0. This produces warnings and can silently produce incorrect results.

5. **Confusing training scripts** — `train_ai_model.py` trains a `LinearSVC` (which does **not** support `predict_proba`), but the actually-deployed model in `agri_svm_model.pkl` is a `LogisticRegression` (trained by `train_model.py`). If anyone re-trains using `train_ai_model.py`, the `/ask` endpoint will **crash** on `predict_proba`.

---

### ⚠️ PARTIALLY WORKING — `POST /ai_timetable` (Timetable Generation)

The endpoint **runs without crashing**, but the generated timetables have quality problems:

**Test: Wheat crop with mixed weather**
```json
Input weather: [Sunny, Rain (15mm), Sunny (35°C)]
Output:
  Day 1: "Day1:Sowing"                              ← raw CSV format leaked
  Day 2: "Rainy: reduce irrigation"                  ← weather rule text, not a task
  Day 3: "Hot day: increase water or give shade"     ← fallback text, not crop-specific
```

#### Issues Found:

1. **Raw CSV format leaks into output** — Normal tasks come through as `"Day1:Sowing"` instead of just `"Sowing"`. The `Day1:` prefix from the CSV is not stripped.

2. **Weather tasks are generic fallbacks** — When no crop-specific hot/cold rules exist, it falls back to generic text like "Hot day: increase water or give shade" instead of crop-tailored advice.

3. **No date format validation** — Sending `start_date: "01-01-2025"` (wrong format) returns HTTP 500 with a Python traceback instead of a helpful error message.

4. **No crop validation** — Unknown crops return `[{"day": 1, "task": "No rules found for this crop"}]` — functional but returns HTTP 200 instead of an error.

5. **Only 13 crops supported** — The `crop_timetable_dataset.csv` only has: Tomato, Onion, Potato, Chilli, Brinjal, Rice, Wheat, Soybean, Cotton, Groundnut, Sugarcane, Maize.

---

### 🔴 BROKEN — LSTM Model Pipeline

- `model/timetable_engine.py` imports from `lstm_service`, but **`lstm_service.py` does not exist** anywhere in the codebase.
- The `agribandhu_lstm_model.h5` file exists but has no loading/inference code.
- The Random Forest model (`agribandhu_rf_model.pkl`) also exists but is not used by the main API.
- `model/api.py` (Flask) and `model/random_api.py` (FastAPI) are **alternative/abandoned API files** that are not connected to the main application.

---

## Part 2: Android App Diagnosis

### 🔴 CRITICAL — Hardcoded Backend IP (Breaks Everything)

The Android app has `http://10.176.21.93:8000` hardcoded in **three places**:
- `ApiClient.java` (line 11)
- `AIChatbot.java` (line 53)
- `crop_actitvty.java` (hardcoded IP)

> ⚠️ **WARNING:** This IP `10.176.21.93` is a **private/local network IP** from the original developer's machine. **All AI features in the Android app will fail** unless you change this to your own machine's IP.

---

### 🔴 CRITICAL — Insecure Authentication

`LoginActivity.java` and `SignUpActivity.java`:
- **Do NOT use Firebase Auth** — passwords are stored in **plain text** in Firebase Realtime Database
- Email is used as a key after replacing `.` with `_` — fragile and non-standard
- `firebase-auth` dependency is **not even included** in `build.gradle.kts`
- Anyone with DB access can read all passwords

---

### 🔴 BROKEN — Community Posts (Image Upload)

`post.java`:
- Images are converted to **Base64 strings** and stored directly in Firebase Realtime Database
- This will cause **massive database bloat**, out-of-memory errors, and quickly exhaust Firebase free-tier quotas
- Should use Firebase Storage instead
- No image compression

---

### 🔴 BROKEN — Crop Activity (Daily AI Actions)

`crop_actitvty.java`:
- Makes OkHttp call to `http://10.176.21.93:8001` (port **8001**, not 8000!)
- There is **no server running on port 8001** — this endpoint doesn't exist
- The crop tracking feature is completely non-functional

---

### ⚠️ PARTIALLY WORKING — AI Chatbot (Timetable Generator)

`AIChatbot.java`:
- Uses deprecated `AsyncTask` for all network calls
- Hardcoded API keys for VisualCrossing Weather and LocationIQ in source code
- Uses outdated SDK version checks (`Build.VERSION_CODES.GINGERBREAD`, API 9)
- **Would work IF** the backend IP is updated to match your machine

---

### ⚠️ PARTIALLY WORKING — AI Q&A Chat

`Ai_chat.java`:
- Only screen that properly uses Retrofit via `ApiClient.java`
- **Would work IF** the backend IP is updated

---

### ⚠️ PARTIALLY WORKING — Weather Page

`weather_page.java`:
- Hardcoded API keys for LocationIQ and VisualCrossing
- Uses raw `OkHttp` instead of Retrofit (inconsistent with rest of app)
- **Would work IF** the API keys are still valid

---

### ⚠️ PARTIALLY WORKING — Government Schemes

`scheme_actitvy.java`:
- Fetches schemes from Firebase for a given date
- **Would work IF** schemes data is populated in Firebase

---

### 🔴 DEAD CODE — Practical Activity

`practical.java`:
- Empty activity — does nothing
- Registered in Manifest but serves no purpose

---

### ⚠️ Build Configuration Issues

`build.gradle.kts`:
- Firebase BOM version `34.5.0` may be invalid/too high — could fail Gradle sync
- `firebase-auth` is absent (because auth is done manually with Realtime DB)
- Network security config only allows cleartext to `10.176.21.93` — will block requests to any other backend IP

---

## Part 3: Hardcoded Secrets

> ⚠️ **SECURITY WARNING:** The following secrets are exposed in plain text in source code:

| Secret | Location | Value |
|--------|----------|-------|
| VisualCrossing API Key | `AIChatbot.java:50`, `weather_page.java` | `CZ8VZ5PCCXU7RHHSYR4GT2QK9` |
| LocationIQ API Key | `AIChatbot.java:51`, `weather_page.java` | `pk.84838c131bfac08c74fb98c5c37aee00` |
| Gemini API Key | `GeminiAPI.java` | Hardcoded |
| Backend IP | `ApiClient.java:11`, `AIChatbot.java:53` | `10.176.21.93` |

---

## Summary: Feature Status Matrix

| # | Feature | Component | Status | Root Cause |
|---|---------|-----------|--------|------------|
| 1 | API Health Check | Backend | ✅ Working | — |
| 2 | AI Q&A (`/ask`) | Backend | ⚠️ Partial | Poor model accuracy, only 7 labels |
| 3 | AI Timetable (`/ai_timetable`) | Backend | ⚠️ Partial | Raw CSV format leaks, generic fallbacks |
| 4 | LSTM Prediction | Backend | 🔴 Broken | `lstm_service.py` missing entirely |
| 5 | Random Forest API | Backend | 🔴 Broken | Not connected to main app |
| 6 | Login / Signup | Android | 🔴 Insecure | Plain-text passwords in DB |
| 7 | AI Chat (Q&A) | Android | 🔴 Broken | Hardcoded wrong IP |
| 8 | AI Timetable Generator | Android | 🔴 Broken | Hardcoded wrong IP |
| 9 | Crop Daily Tracking | Android | 🔴 Broken | Wrong port (8001), no server exists |
| 10 | Community Posts | Android | 🔴 Broken | Base64 images in Realtime DB |
| 11 | Weather Dashboard | Android | ⚠️ Partial | Hardcoded keys, may still work |
| 12 | Government Schemes | Android | ⚠️ Partial | Depends on Firebase data population |
| 13 | Practical Activity | Android | 🔴 Dead | Empty, unused |

---

## Recommended Priority Fixes

1. **Update hardcoded IP** in `ApiClient.java`, `AIChatbot.java`, `crop_actitvty.java` to your machine's IP (or use `BuildConfig`)
2. **Fix network security config** in `AndroidManifest.xml` to allow your IP
3. **Fix port mismatch** in `crop_actitvty.java` (8001 → 8000)
4. **Re-train the AI model** with current sklearn version and more response categories
5. **Add confidence threshold** to `/ask` to return "I don't know" for low-confidence predictions
6. **Strip "DayN:" prefix** from timetable CSV data in `dataset_loader.py`
7. **Replace plain-text auth** with Firebase Auth
8. **Move image uploads** from Realtime DB to Firebase Storage
9. **Create `lstm_service.py`** or remove the LSTM references
10. **Move API keys** to environment variables / `local.properties`
