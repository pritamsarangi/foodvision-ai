from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import get_optional_current_user
from app.core.database import SessionLocal
from app.models.prediction import Prediction
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/predictions",
    tags=["Prediction History"],
)


@router.get("")
def get_predictions(current_user: Optional[User] = Depends(get_optional_current_user)):
    try:
        with SessionLocal() as db:
            # Set transaction-local RLS user context
            user_id = current_user.id if current_user else ""
            db.execute(text("SET LOCAL app.current_user_id = :uid"), {"uid": user_id})

            # Application-level query filter (Defense-in-depth)
            query = select(Prediction).order_by(Prediction.created_at.desc()).limit(100)
            if current_user:
                query = query.where(Prediction.user_id == current_user.id)
            else:
                query = query.where(Prediction.user_id.is_(None))

            records = db.scalars(query).all()
            return jsonable_encoder(records)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Prediction history temporarily unavailable",
        )


@router.get("/{prediction_id}")
def get_prediction(
    prediction_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    try:
        with SessionLocal() as db:
            user_id = current_user.id if current_user else ""
            db.execute(text("SET LOCAL app.current_user_id = :uid"), {"uid": user_id})

            record = db.get(Prediction, prediction_id)
            if record is None:
                raise HTTPException(
                    status_code=404,
                    detail="Prediction not found",
                )

            # Prevent cross-user record inspection
            if record.user_id and (not current_user or record.user_id != current_user.id):
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