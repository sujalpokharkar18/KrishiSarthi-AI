# api/main.py — KrishiSarthi AI FastAPI Server

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time
import logging

from ai_engine import predict_label, get_response_for_label
from timetable_engine import generate_timetable
from dataset_loader import get_supported_crops, normalize_crop_name
from prediction_service import predict_action
from crop_doctor import diagnose_crop_photo

# ─── Structured Server-Side Logging ──────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("krishisarthi")

app = FastAPI(
    title="KrishiSarthi AI",
    version="2.0",
    description="Smart Agricultural Assistant: AI Intent Answering, Weather-Aware Timetables, and Prediction API"
)


# ─── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request Latency & Audit Logging Middleware ──────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"

    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"{request.method} {request.url.path} | "
            f"status={response.status_code} | "
            f"client={client_host} | "
            f"latency={duration_ms}ms"
        )
        return response
    except Exception as exc:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"FAIL {request.method} {request.url.path} | "
            f"client={client_host} | "
            f"latency={duration_ms}ms | "
            f"error={exc}",
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing your request.",
                "status_code": 500
            }
        )


# ─── Request Models with Input Constraints ───────────────────

class Query(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Agricultural question (1-1000 characters)"
    )


class TimetableRequest(BaseModel):
    crop: str = Field(
        ...,
        min_length=1,
        max_length=60,
        description="Target crop name (e.g. 'Wheat' or 'Tomato')"
    )
    start_date: str = Field(
        ...,
        min_length=8,
        max_length=15,
        description="Start date in YYYY-MM-DD format (e.g. '2026-09-03')"
    )
    weather: list = Field(
        ...,
        min_length=1,
        max_length=31,
        description="List of daily forecast dicts (1 to 31 days)"
    )


class DiagnosisRequest(BaseModel):
    image_base64: str = Field(default="", description="Base64 encoded crop photo")
    crop_name: str = Field(default="", description="Crop name if known (e.g. 'tomato')")
    notes: str = Field(default="", description="Farmer's observation or symptoms")


# ─── Custom Exception Handlers ───────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats Pydantic 422 validation errors into user-friendly JSON."""
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", [])])
        msg = err.get("msg", "Invalid value")
        errors.append(f"{loc}: {msg}")

    detail_message = "; ".join(errors) if errors else "Invalid request body structure."
    logger.warning(f"Validation failed on {request.url.path}: {detail_message}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": detail_message,
            "status_code": 422
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Formats explicit HTTPExceptions consistently."""
    logger.info(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Bad Request" if exc.status_code == 400 else "Request Error",
            "message": str(exc.detail),
            "detail": str(exc.detail),  # Maintained for Android backwards compatibility
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches any unhandled Python exception, logs trace server-side, hides it from client."""
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something went wrong while processing the request. Please try again later.",
            "status_code": 500
        }
    )


# ─── API Routes ──────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "KrishiSarthi AI API running",
        "version": "2.0",
        "endpoints": ["/ask", "/ai_timetable", "/predict", "/diagnose_crop"],
        "supported_crops": get_supported_crops()
    }


@app.post("/ask")
def ask(query: Query):
    """
    Classify a farming question and return an AI-generated response.
    Returns UNKNOWN for low-confidence or non-farming questions.
    """
    cleaned_q = query.question.strip()
    if not cleaned_q:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    label, confidence = predict_label(cleaned_q)
    reply = get_response_for_label(label)

    return {
        "question": cleaned_q,
        "label": label,
        "confidence": round(float(confidence), 4),
        "answer": reply,
        "reply": reply  # Maintained for Android AnswerResponse compatibility
    }


@app.post("/ai_timetable")
def ai_timetable(req: TimetableRequest):
    """
    Generate a weather-aware farming timetable for the given crop.
    Validates crop name, start_date format, and weather forecast length.
    """
    raw_crop = req.crop.strip()
    if not raw_crop:
        raise HTTPException(status_code=400, detail="Crop name is required.")

    canonical_crop = normalize_crop_name(raw_crop)

    # Validate date format
    start_date_str = req.start_date.strip()
    try:
        datetime.strptime(start_date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid start_date format '{req.start_date}'. Expected format: YYYY-MM-DD (e.g. 2026-09-03)"
        )

    if not req.weather or len(req.weather) == 0:
        raise HTTPException(status_code=400, detail="Weather forecast list cannot be empty.")

    try:
        timetable = generate_timetable(
            crop=canonical_crop,
            start_date=start_date_str,
            weather=req.weather
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "crop": canonical_crop.capitalize(),
        "start_date": start_date_str,
        "timetable": timetable
    }


@app.post("/predict")
def predict(
    temp: float = 28.0,
    humidity: float = 60.0,
    rain: float = 0.0,
    wind: float = 5.0,
    crop_stage: int = 1,
    date: str = ""
):
    """
    Predict daily agricultural action using Random Forest model.
    Accepts weather parameters (temp, humidity, rain, wind), crop_stage (0-3), and date.
    Directly consumed by Android crop_actitvty.java.
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    return predict_action(
        temp=temp,
        humidity=humidity,
        rain=rain,
        wind=wind,
        crop_stage=crop_stage,
        date=date
    )


@app.get("/predict")
def predict_get(
    temp: float = 28.0,
    humidity: float = 60.0,
    rain: float = 0.0,
    wind: float = 5.0,
    crop_stage: int = 1,
    date: str = ""
):
    """GET variant of /predict for quick browser testing."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    return predict_action(
        temp=temp,
        humidity=humidity,
        rain=rain,
        wind=wind,
        crop_stage=crop_stage,
        date=date
    )


@app.post("/diagnose_crop")
def diagnose_crop(req: DiagnosisRequest):
    """
    Diagnose crop health and diseases from a photo and notes.
    Analyzes visual indicators and descriptions to return tailored symptoms,
    immediate agronomic actions, organic remedies, and chemical spray dosages.
    """
    try:
        result = diagnose_crop_photo(
            image_base64=req.image_base64,
            crop_name=req.crop_name,
            user_notes=req.notes
        )
        return {
            "status": "success",
            "diagnosis": result
        }
    except Exception as e:
        logger.error(f"Error in /diagnose_crop: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
