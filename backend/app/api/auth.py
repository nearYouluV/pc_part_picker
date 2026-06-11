from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
import os

from ..database import get_db
from ..auth_schemas import UserCreate, UserLogin, UserResponse, Token, RefreshTokenRequest
from ..services.auth_service import (
    get_user_by_username,
    normalize_username,
    hash_refresh_token,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_active_user,
    get_user_by_email,
    normalize_email,
    create_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from ..services.brute_force_protection import (
    handle_failed_login_attempt,
    handle_successful_login,
    validate_login_attempt,
)
from ..utils.rate_limit import per_ip_rate_limit
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


REGISTER_RATE_LIMIT = int(os.getenv("REGISTER_RATE_LIMIT", "5"))
REGISTER_RATE_WINDOW_SECONDS = int(os.getenv("REGISTER_RATE_WINDOW_SECONDS", "60"))
LOGIN_RATE_LIMIT = int(os.getenv("LOGIN_RATE_LIMIT", "10"))
LOGIN_RATE_WINDOW_SECONDS = int(os.getenv("LOGIN_RATE_WINDOW_SECONDS", "60"))
REFRESH_RATE_LIMIT = int(os.getenv("REFRESH_RATE_LIMIT", "20"))
REFRESH_RATE_WINDOW_SECONDS = int(os.getenv("REFRESH_RATE_WINDOW_SECONDS", "60"))

register_rate_limiter = per_ip_rate_limit(
    bucket="auth:register",
    limit=REGISTER_RATE_LIMIT,
    window_seconds=REGISTER_RATE_WINDOW_SECONDS,
)
login_rate_limiter = per_ip_rate_limit(
    bucket="auth:login",
    limit=LOGIN_RATE_LIMIT,
    window_seconds=LOGIN_RATE_WINDOW_SECONDS,
)
refresh_rate_limiter = per_ip_rate_limit(
    bucket="auth:refresh",
    limit=REFRESH_RATE_LIMIT,
    window_seconds=REFRESH_RATE_WINDOW_SECONDS,
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _: None = Depends(register_rate_limiter),
):
    """Register a new user"""
    normalized_email = normalize_email(user_data.email)
    normalized_username = normalize_username(user_data.username)

    if get_user_by_username(db, normalized_username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    if get_user_by_email(db, normalized_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    user = create_user(
        db=db,
        email=normalized_email,
        username=normalized_username,
        password=user_data.password
    )

    return user


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    _: None = Depends(login_rate_limiter),
):
    """Login and get access token + refresh token"""
    identifier = user_credentials.identifier.strip().lower()
    user = get_user_by_email(db, identifier)
    if not user:
        user = get_user_by_username(db, identifier)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is locked due to brute force attempts
    validate_login_attempt(db, user)

    # Verify password
    from ..services.auth_service import verify_password
    if not verify_password(user_credentials.password, user.hashed_password):
        # Record the failed attempt
        handle_failed_login_attempt(db, user)

    # Successful authentication - reset failed attempts
    handle_successful_login(db, user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )

    user.refresh_token = hash_refresh_token(refresh_token)
    user.refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_request: RefreshTokenRequest,
    db: Session = Depends(get_db),
    _: None = Depends(refresh_rate_limiter),
):
    """Refresh access token using refresh token"""
    user = verify_refresh_token(db, token_request.refresh_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )

    new_refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )

    user.refresh_token = hash_refresh_token(new_refresh_token)
    user.refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout and invalidate refresh token"""
    current_user.refresh_token = None
    current_user.refresh_token_expires = None
    db.commit()

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
