from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.rate_limit import RateLimiter

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(limit=3, window_seconds=3600, prefix="rl:auth:register"))],
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user account."""
    return auth_service.register_user(db, user_in)


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(RateLimiter(limit=5, window_seconds=60, prefix="rl:auth:login"))],
)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user and returns an access/refresh token pair."""
    user = auth_service.authenticate_user(db, login_in.email, login_in.password)
    return auth_service.create_token_pair(db, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Rotates refresh token and returns a fresh access/refresh token pair."""
    return auth_service.rotate_refresh_token(db, request.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Revokes the refresh token."""
    auth_service.revoke_token(db, request.refresh_token)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile."""
    return current_user