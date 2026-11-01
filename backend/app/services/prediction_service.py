
import uuid

from app.core.database import SessionLocal
from app.models.prediction import Prediction


def save_prediction(
    food_name: str,
    confidence: float,
    top_5: list,
    model_version: str,
):
    prediction = Prediction(
        id=str(uuid.uuid4()),
        food_name=food_name,
        confidence=confidence,
        top_5=top_5,
        model_version=model_version,
    )

    with SessionLocal() as db:
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return prediction
