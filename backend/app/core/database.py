from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

if not settings.database_url:
    raise RuntimeError("DATABASE_URL is missing from configuration")

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()