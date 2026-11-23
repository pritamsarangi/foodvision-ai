from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_secure_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.user import RefreshToken, User
from app.schemas.auth import TokenResponse, UserCreate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieves a user by normalized email."""
    return db.scalar(select(User).where(User.email == email.lower().strip()))


def register_user(db: Session, user_in: UserCreate) -> User:
    """Registers a new user with Argon2id hashed password."""
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        email=user_in.email.lower().strip(),
        hashed_password=hash_password(user_in.password),
        role="user",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Verifies credentials and returns user or raises 401."""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return user


def create_token_pair(db: Session, user: User) -> TokenResponse:
    """Issues a new JWT access token and records a hashed refresh token."""
    access_token = create_access_token(subject=user.id, role=user.role)
    raw_refresh_token = generate_secure_token()

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.refresh_token_expire_days)

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(raw_refresh_token),
        expires_at=expires_at,
        revoked=False,
    )
    db.add(db_token)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
    )


def rotate_refresh_token(db: Session, raw_token: str) -> TokenResponse:
    """Rotates refresh token. Implements automatic reuse detection."""
    token_digest = hash_token(raw_token)
    token_record = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_digest)
    )

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # REUSE DETECTION: If this token was already revoked, an attack is occurring!
    if token_record.revoked:
        # Revoke the entire token family for this user
        db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == token_record.user_id)
            .values(revoked=True)
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token reuse detected. All sessions revoked for security.",
        )

    # Check expiration
    now = datetime.now(timezone.utc)
    if token_record.expires_at < now:
        token_record.revoked = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    # Invalidate the used token
    token_record.revoked = True

    # Issue a brand new token pair
    user = db.get(User, token_record.user_id)
    if not user or not user.is_active:
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer active",
        )

    new_access_token = create_access_token(subject=user.id, role=user.role)
    new_raw_refresh = generate_secure_token()

    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_raw_refresh),
        parent_token_hash=token_digest,
        expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        revoked=False,
    )
    db.add(new_token_record)
    db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_raw_refresh,
    )


def revoke_token(db: Session, raw_token: str) -> None:
    """Revokes an active refresh token (user logout)."""
    token_digest = hash_token(raw_token)
    token_record = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_digest)
    )
    if token_record and not token_record.revoked:
        token_record.revoked = True
        db.commit()