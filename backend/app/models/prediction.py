
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True)
    #Foreign key linking prediction so authenticated user (nullable=True allows legacy/guest predictions)
    user_id = Column(String(36),ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    food_name = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    top_5 = Column(JSON, nullable=False)
    model_version = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="predictions")
