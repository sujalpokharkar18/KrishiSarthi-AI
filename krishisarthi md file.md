# KrishiSarthi : Path To Smart Farming
## Comprehensive Project Documentation & Sprint Tracking Master Document (v2.0 - Review 2)

---

## 1. Project Identification & Metadata

| Field | Detail |
| :--- | :--- |
| **Project Name** | **KrishiSarthi : Path To Smart Farming** |
| **Project ID / Group Code** | **TYDA01** |
| **Academic Level** | B.Tech SEM 5 — Project Based Learning (PBL) |
| **Review Milestone** | **Review 2 (09 October 2026)** |
| **Project Development Window** | **01 August 2026 – 08 October 2026** |
| **Primary Authors / Team** | Sujal Pokharkar & Team TYDA01 |
| **Platform Target** | Android Mobile App (Native Java) + Python AI Microservice |
| **Current Build Status** | Stable (`BUILD SUCCESSFUL` - 0 Errors, Debug APK Compiled) |

---

## 2. Executive Summary & Problem Statement

Traditional agricultural workflows in India suffer from fragmented information access:
1. **Unpredictable Weather & Inefficient Scheduling:** Farmers lack dynamic, hyper-local timetable recommendations tailored to current crop growth stages.
2. **Delayed Pathology Diagnosis:** Identifying plant leaf diseases and pests often requires physical agricultural officers, causing yield loss before remedies are applied.
3. **Fragmented Record Keeping:** Multi-crop farmers cannot track sowing dates, required daily farming interventions, and land allocations in a unified mobile dashboard.
4. **General-Purpose AI Hallucination:** Standard chatbots give irrelevant non-agricultural answers or lack regional crop knowledge.

**KrishiSarthi** solves these challenges by combining:
* **Native Android Mobile Client (`KrishiSarthi`):** Clean farmer-centric UI featuring a visual dashboard, multi-crop tracking with real produce photography, community crop post sharing, and account switching.
* **FastAPI Python AI Microservice:** Intent classification, crop pathology diagnosis from leaf photographs, and daily farming recommendations.
* **Random Forest ML Engine:** Daily action predictions (Sowing, Irrigation, Fertilizer, Pesticide, Wait) based on humidity, temperature, precipitation, and vegetative growth stages.
* **Cloud & Realtime Sync:** Firebase Authentication and Realtime Database for farm profile data, community feed, and crop progress.

---

## 3. Supported Crops (12 Agricultural Produce)

KrishiSarthi provides end-to-end dataset coverage, daily action models, AI guidance, and UI visual assets for **12 prominent crops**:

| No. | Crop Name | Regional / Alias Names Supported | Dedicated Visual Asset | Growth Stage Range |
| :---: | :--- | :--- | :---: | :---: |
| 1 | **Onion** | Pyaz, Kanda | `onion.png` | 90 – 150 Days |
| 2 | **Tomato** | Tamatar | `tomato.png` | 60 – 100 Days |
| 3 | **Wheat** | Gehu, Gehun | `wheat.png` | 100 – 140 Days |
| 4 | **Potato** | Aloo, Batata | `potato.png` | 75 – 120 Days |
| 5 | **Rice** | Paddy, Chawal, Dhan | `rice.png` | 100 – 150 Days |
| 6 | **Maize** | Corn, Makka, Bhutta | `maize.png` | 80 – 120 Days |
| 7 | **Cotton** | Kapas | `cotton.png` | 140 – 180 Days |
| 8 | **Soybean** | Soya, Soyabean | `soybean.png` | 85 – 110 Days |
| 9 | **Sugarcane** | Ganna, Ikshu | `sugarcane.png` | 300 – 360 Days |
| 10 | **Chilli** | Chili, Mirchi, Mirch | `chilli.png` | 90 – 150 Days |
| 11 | **Brinjal** | Eggplant, Baingan, Vangi | `brinjal.png` | 100 – 140 Days |
| 12 | **Groundnut** | Peanut, Mungfali, Shengdana | `groundnut.png` | 100 – 130 Days |

---

## 4. End-to-End System Architecture

```
                    ┌─────────────────────────────────────────────────────┐
                    │               Android App (KrishiSarthi)            │
                    │   • Farmer Profile & Active Crops Dashboard         │
                    │   • AI Advisory Chatbot (Natural Query Interface)   │
                    │   • Weather-Aware Timetable Generator               │
                    │   • Community Post & Crop Photo Diagnosis           │
                    └───────────┬─────────────────────────┬───────────────┘
                                │                         │
                   REST Calls   │                         │ Firebase SDK
                 (Retrofit/OkHttp)                        │ (Auth & RTDB)
                                │                         │
                                ▼                         ▼
        ┌────────────────────────────────────┐  ┌─────────────────────────┐
        │       Cloudflare Secure Tunnel     │  │   Firebase Cloud Backend│
        │  (HTTPS Reverse Proxy bom06/bom10) │  │  • Farmer Authentication│
        └─────────────────┬──────────────────┘  │  • Multi-Crop Progress  │
                          │                     │  • Social Feed Posts    │
                          ▼                     └─────────────────────────┘
        ┌─────────────────────────────────────────────────────────────────┐
        │               Python Microservice (FastAPI + Uvicorn)           │
        │                                                                 │
        │  ┌───────────────────────┐   ┌───────────────────────────────┐  │
        │  │   ai_engine.py        │   │       crop_doctor.py          │  │
        │  │ TF-IDF + Logistic     │   │ PIL RGB Color Histogram &     │  │
        │  │ Classifier (12 Intents│   │ Heuristic Diagnostic Engine   │  │
        │  │ + UNKNOWN Out-of-Scope│   │ (Blight, Rust, Powdery Mildew)│  │
        │  └───────────────────────┘   └───────────────────────────────┘  │
        │  ┌───────────────────────┐   ┌───────────────────────────────┐  │
        │  │  timetable_engine.py  │   │     prediction_service.py     │  │
        │  │ Visual Crossing API   │   │ Random Forest Classifier      │  │
        │  │ + Agronomic Rules     │   │ (agribandhu_rf_model.pkl)     │  │
        │  └───────────────────────┘   └───────────────────────────────┘  │
        └─────────────────────────────────────────────────────────────────┘
```

---

## 5. Timeline, Sprints & Tracker Sheet Task Mapping (Aug 1 – Oct 8, 2026)

This section maps project milestones directly to Agile Sprints for project trackers and evaluation rubrics.

### Sprint 1: Requirements Engineering & Foundation Setup (01 Aug 2026 – 14 Aug 2026)
* **Goal:** Finalize smart farming scope, establish Android and Python architectures, integrate Firebase authentication.
* **Key Tasks:**
  1. Define agronomic domain scope covering small and marginal Indian farmers.
  2. Initialize native Android project with Material 3 styling and Gradle configuration.
  3. Configure Firebase project, SHA-1 fingerprints, and `google-services.json` authentication rules.
  4. Build `LoginActivity` and `SignUpActivity` with email/password validation and session caching.
  5. Set up FastAPI Python backend scaffolding on port 8000 with CORS middleware.

### Sprint 2: Core Machine Learning & Dataset Pipeline (15 Aug 2026 – 31 Aug 2026)
* **Goal:** Synthesize multi-crop agricultural datasets, train intent classifier and Random Forest prediction models.
* **Key Tasks:**
  1. Construct expanded training and testing datasets (`train_expanded.csv`, `test_expanded.csv`) spanning 12 major crops.
  2. Build `train_classifier.py` implementing TF-IDF vectorization with Logistic Regression/SVM for query classification.
  3. Train Random Forest model (`agribandhu_rf_model.pkl`) to predict daily farming actions based on temperature, rainfall, and vegetative stage.
  4. Implement strict out-of-scope filtering (`UNKNOWN` intent) so economic/market questions or non-farming queries are correctly flagged.
  5. Benchmark classification metrics achieving >92% test accuracy on multi-intent agriculture queries.

### Sprint 3: AI Chatbot, Timetable Engine & Weather Integration (01 Sep 2026 – 16 Sep 2026)
* **Goal:** Connect mobile client to live weather APIs and develop dynamic timetable generation.
* **Key Tasks:**
  1. Integrate Visual Crossing Weather API for real-time geographic temperature, rainfall, and humidity lookups.
  2. Implement `AIChatbot.java` and `timetable_engine.py` to produce weekly weather-adapted schedules.
  3. Develop `Ai_chat.java` conversational UI with message bubbles, loading animations, and retry mechanisms.
  4. Create `ApiClient.java` with centralized Retrofit/OkHttp singletons and automatic gateway retry policies.
  5. Deploy secure HTTP/2 tunnel via `cloudflared.exe` enabling real-device testing without static IPs.

### Sprint 4: Visual Dashboard, Multi-Crop Tracking & Plant Pathology (17 Sep 2026 – 30 Sep 2026)
* **Goal:** Build rich farmer profile dashboard, image diagnosis engine, and community post sharing.
* **Key Tasks:**
  1. Implement `Main_Account.java` dashboard showing farmer acreage, monthly revenue, and active crops.
  2. Add community photo sharing (`post.java`, `PostAdapter.java`) with Firebase Realtime Database storage.
  3. Build `crop_doctor.py` computer vision diagnosis engine evaluating leaf symptoms and recommending chemical/organic remedies.
  4. Design `crop_actitvty.java` displaying live vegetative stage tracking and automated daily notifications.
  5. Add multi-account switching dialog allowing family farm accounts to toggle seamlessly without cache corruption.

### Sprint 5: Project Polishing, KrishiSarthi Rebranding & Final Verification (01 Oct 2026 – 08 Oct 2026)
* **Goal:** Complete rebranding to KrishiSarthi, fix image rendering bottlenecks, build clean production APK for Review 2.
* **Key Tasks:**
  1. Rename all user-facing strings, headers, dialogue titles, and API responses across frontend and backend to **KrishiSarthi**.
  2. Download and curate high-resolution visual assets for all 12 crops (`onion.png`, `potato.png`, `rice.png`, etc.) in `res/drawable`.
  3. Upgrade dynamic crop image matcher in `Main_Account.java` with regional aliases (`kanda`, `pyaz`, `aloo`, `makka`, `mirchi`).
  4. Rebrand launcher icon `app_icon.png` with clean KrishiSarthi branding.
  5. Validate full Gradle assembly (`BUILD SUCCESSFUL in 29s`), verify live Cloudflare HTTPS tunnel, and generate final documentation.

---

## 6. Core Features & Functional Modules

### Module A: Farmer Profile & Active Crop Dashboard
* **Screen:** `Main_Account.java` (`activity_main_account.xml`)
* **Features:**
  * Displays farmer name, verified location, land size (in acres), and estimated monthly income.
  * Dynamically populates horizontal cards for every crop currently under cultivation.
  * Automatic image allocation for 12 crops based on name normalization.
  * One-tap navigation to deep crop action views (`crop_actitvty.java`).
  * Account switcher dialog with clean session reset.

### Module B: AI Advisory Chatbot (`Ai_chat.java`)
* **Screen:** `Ai_chat.java` (`activity_ai_chat.xml`)
* **Features:**
  * Natural language question answering tuned exclusively for farming queries.
  * Direct HTTP POST communication to `/ask` endpoint on FastAPI.
  * Built-in fallback detection: when out-of-scope or economic questions are asked (e.g., onion market prices), the system politely guides the farmer to ask agricultural and crop health questions.

### Module C: Weather-Aware Crop Timetable Generator
* **Screen:** `AIChatbot.java` (`activity_aichatbot.xml`)
* **Features:**
  * Farmer enters geographic area/city and crop type.
  * Live weather retrieval via Visual Crossing API (coordinates, 7-day rainfall, temperature, soil humidity).
  * Backend AI computes stage-specific milestones (land preparation, seed treatment, irrigation, basal fertilizer, harvesting).
  * Instant "Save Crop Progress" button directly writes active crop tracking to Firebase under the farmer's account.

### Module D: Plant Pathology & Crop Doctor (`post.java`)
* **Screen:** `post.java` (`activity_post.xml`)
* **Features:**
  * Farmer uploads or captures photo of an unhealthy leaf/plant.
  * "🔬 Analyzing Photo with KrishiSarthi AI..." sends image payload to `/diagnose_crop`.
  * Returns identified diagnosis, pathogen classification, severity level, dosage recommendations, and organic alternatives.

---

## 7. Machine Learning Models & Backend API Specifications

### Backend Endpoints (FastAPI)

#### 1. `GET /`
* **Purpose:** Health check & capability introspection.
* **Sample Response:**
```json
{
  "message": "KrishiSarthi AI API running",
  "version": "2.0",
  "endpoints": ["/ask", "/ai_timetable", "/predict", "/diagnose_crop"],
  "supported_crops": ["brinjal", "chilli", "cotton", "groundnut", "maize", "onion", "potato", "rice", "soybean", "sugarcane", "tomato", "wheat"]
}
```

#### 2. `POST /ask`
* **Payload:** `{"query": "How much urea should I add to wheat in tillering stage?"}`
* **Response:** Predicted intent label, confidence score, and structured response text.

#### 3. `POST /ai_timetable`
* **Payload:** `{"crop_name": "Onion", "city": "Pune", "start_date": "2026-10-08"}`
* **Response:** Formatted 5-stage agronomic schedule with temperature and irrigation advisories.

#### 4. `POST /predict`
* **Payload:** `{"crop_name": "Onion", "crop_stage": 1, "temp": 28.5, "humidity": 72.0, "rainfall": 2.5}`
* **Response:** Action prediction (`Sowing`, `Irrigation`, `Fertilizer`, `Pesticide`, or `Wait`).

#### 5. `POST /diagnose_crop`
* **Payload:** Multipart image file or base64 photo with symptom text.
* **Response:** Diagnostic name, severity, dosage, and preventive management tips.

---

## 8. Android Application Structure

```
android_app/app/src/main/
├── AndroidManifest.xml              # Launcher config, Internet & Storage permissions
├── java/com/example/agribandhu/     # Internal namespace preserved for Gradle stability
│   ├── AIChatbot.java               # Weather fetching & Timetable AI engine
│   ├── Ai_chat.java                 # Conversational Q&A chat interface
│   ├── crop_actitvty.java           # Daily crop action & stage viewer
│   ├── LoginActivity.java           # Farmer login & session manager
│   ├── SignUpActivity.java          # New farmer registration
│   ├── MainActivity.java            # Home navigation hub
│   ├── Main_Account.java            # Visual farmer dashboard & 12-crop mapper
│   ├── post.java                    # Community posting & Crop Doctor upload
│   ├── PostAdapter.java             # RecyclerView adapter for social feed
│   ├── practical.java               # Camera & gallery diagnostic utility
│   ├── weather_page.java            # Live weather radar & forecast
│   └── network/
│       └── ApiClient.java           # OkHttp + Retrofit HTTP/2 connection client
└── res/
    ├── drawable/
    │   ├── onion.png                # High-res produce photo
    │   ├── tomato.png               # High-res produce photo
    │   ├── wheat.png                # High-res produce photo
    │   ├── potato.png               # High-res produce photo
    │   ├── rice.png                 # High-res produce photo
    │   ├── maize.png                # High-res produce photo
    │   ├── cotton.png               # High-res produce photo
    │   ├── soybean.png              # High-res produce photo
    │   ├── sugarcane.png            # High-res produce photo
    │   ├── chilli.png               # High-res produce photo
    │   ├── brinjal.png              # High-res produce photo
    │   ├── groundnut.png            # High-res produce photo
    │   └── app_icon.png             # Updated KrishiSarthi branding icon
    ├── layout/
    │   ├── activity_main_account.xml# Farmer dashboard layout
    │   ├── item_crop_card.xml       # Horizontal crop produce card
    │   ├── activity_ai_chat.xml     # AI Assistant interface
    │   ├── activity_aichatbot.xml   # Timetable input interface
    │   └── activity_post.xml        # Community & Pathology layout
    └── values/
        ├── strings.xml              # app_name = "KrishiSarthi"
        └── colors.xml               # Agricultural green theme palette
```

---

## 9. Verification & Review 2 Readiness Checklist

| Verification Item | Status | Verified Evidence |
| :--- | :---: | :--- |
| **App Name & Display** | ✅ Pass | `strings.xml` set to `KrishiSarthi`; phone launcher shows KrishiSarthi |
| **Screen Titles & Toolbars** | ✅ Pass | All toolbars in Login, Signup, Dashboard, AI Chat display KrishiSarthi |
| **Crop Image Library** | ✅ Pass | All 12 crops have dedicated 400x400 PNG produce photos in `res/drawable` |
| **Onion Image Rendering** | ✅ Pass | `Main_Account.java` dynamically binds `R.drawable.onion` for Onion/Pyaz/Kanda |
| **Fallback Asset Cleanup** | ✅ Pass | `item_crop_card.xml` default src changed from app logo to `@drawable/wheat` |
| **FastAPI Backend Server** | ✅ Pass | `api/main.py` responds with `"KrishiSarthi AI API running"` on `/` |
| **Cloudflare Tunnel Proxy** | ✅ Pass | HTTP/2 HTTPS tunnel routes live mobile traffic to local backend |
| **Gradle Compilation** | ✅ Pass | `./gradlew assembleDebug` passed with 0 errors in 29 seconds |
| **Debug APK Available** | ✅ Pass | `app-debug.apk` built and ready for physical device deployment |

---

*Document compiled and verified for Group TYDA01 Review 2 Presentation (09 October 2026).*
