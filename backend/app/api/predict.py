
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.prediction import Prediction

router = APIRouter(
    prefix="/api/v1/predictions",
    tags=["Prediction History"],
)



@router.get("")
def get_predictions():
    try:
        with SessionLocal() as db:
            records = db.scalars(
                select(Prediction)
                .order_by(Prediction.created_at.desc())
                .limit(100)
            ).all()

            return jsonable_encoder(records)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Prediction history temporarily unavailable",
        )


@router.get("/{prediction_id}")
def get_prediction(prediction_id: str):
    try:
        with SessionLocal() as db:
            record = db.get(Prediction, prediction_id)

            if record is None:
                raise HTTPException(
                    status_code=404,
                    detail="Prediction not found",
                )

            return jsonable_encoder(record)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Prediction history temporarily unavailable",
        )
