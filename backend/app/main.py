from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from typing import Optional
from app.api.predict import router as predictions_router
from fastapi.concurrency import run_in_threadpool
from app.services.inference import predict_image
from app.services.prediction_service import save_prediction
from app.services.inference import load_model
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI(title="FoodVision AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(predictions_router)
MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


class FoodPrediction(BaseModel):
    food_name: str
    confidence: float


class PredictionResponse(BaseModel):
    prediction_id: Optional[str] = None
    food_name: str
    confidence: float
    top_5: list[FoodPrediction]
    model_version: str
    is_mock: bool


@app.get("/api/v1/health")
def health():
    return {"status": "ok","model_loaded": load_model.cache_info().currsize > 0,
            }


@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WebP image")
    data = await file.read(MAX_IMAGE_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Image is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB")

    # Run real EfficientNet-B0 inference
    try:
        top_5 = await run_in_threadpool(
            predict_image,
            data,
        )
    except (OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported image",
        )

    # Store real prediction in Neon PostgreSQL
    
    try:
        saved = await run_in_threadpool(
            save_prediction,
            food_name=top_5[0]["food_name"],
            confidence=top_5[0]["confidence"],
            top_5=top_5,
            model_version="efficientnet-b0-finetuned-v1",
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Prediction storage temporarily unavailable",
        )


    return PredictionResponse(
        prediction_id=saved.id,
        food_name=top_5[0]["food_name"],
        confidence=top_5[0]["confidence"],
        top_5=top_5,
        model_version="efficientnet-b0-finetuned-v1",
        is_mock=False,
    )
