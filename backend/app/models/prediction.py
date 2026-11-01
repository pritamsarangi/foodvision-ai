
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, DateTime, JSON
from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True)
    food_name = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    top_5 = Column(JSON, nullable=False)
    model_version = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
