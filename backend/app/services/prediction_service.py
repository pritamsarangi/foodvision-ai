import uuid
from typing import Optional
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.prediction import Prediction


def save_prediction(
    food_name: str,
    confidence: float,
    top_5: list,
    model_version: str,
    user_id: Optional[str] = None,
):
    prediction = Prediction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        food_name=food_name,
        confidence=confidence,
        top_5=top_5,
        model_version=model_version,
    )

    with SessionLocal() as db:
        # Set session context for PostgreSQL RLS
        db.execute(text("SET LOCAL app.current_user_id = :uid"), {"uid": user_id or ""})
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return prediction