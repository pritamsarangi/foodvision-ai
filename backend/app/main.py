from typing import Optional
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.predict import router as predictions_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.inference import load_model, predict_image
from app.services.prediction_service import save_prediction
from app.api.auth import router as auth_router
from app.api.deps import get_optional_current_user
from app.models.user import User

app = FastAPI(title=settings.app_name, version=settings.app_version)

# 1. CORS Middleware using centralized settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(predictions_router)
app.include_router(auth_router)

# 2. Schemas
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


# 3. Health & Observability Probes
@app.get("/api/v1/health")
def health():
    """Backward-compatible health endpoint."""
    return {
        "status": "ok",
        "model_loaded": load_model.cache_info().currsize > 0,
    }


@app.get("/api/v1/health/live", status_code=status.HTTP_200_OK)
def liveness():
    """Liveness probe: verifies process is alive."""
    return {"status": "alive"}


@app.get("/api/v1/health/ready")
def readiness():
    """Readiness probe: verifies database connectivity and model availability."""
    checks = {
        "database": False,
        "model_weights": False,
        "model_cached": load_model.cache_info().currsize > 0,
    }

    # Verify DB connectivity
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # Verify weights file exists on disk
    weights_path = (
        settings.project_root
        / "ml"
        / "experiments"
        / "efficientnet_b0"
        / "best_finetuned_weights.h5"
    )
    checks["model_weights"] = weights_path.exists()

    if not checks["database"] or not checks["model_weights"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "checks": checks},
        )

    return {"status": "ready", "checks": checks}


# 4. Predict Endpoint using centralized settings
@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...),
                  current_user: Optional[User] = Depends(get_optional_current_user)
                  ):
    if file.content_type not in settings.allowed_image_types:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WebP image")
    data = await file.read(settings.max_image_bytes + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Image is empty")
    if len(data) > settings.max_image_bytes:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB")

    # Run EfficientNet-B0 inference on threadpool
    try:
        top_5 = await run_in_threadpool(predict_image, data)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (OSError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid or unsupported image")

    # Store prediction in PostgreSQL
    try:
        saved = await run_in_threadpool(
            save_prediction,
            food_name=top_5[0]["food_name"],
            confidence=top_5[0]["confidence"],
            top_5=top_5,
            model_version=settings.model_version,
            user_id=current_user.id if current_user else None,
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
        model_version=settings.model_version,
        is_mock=False,
    )