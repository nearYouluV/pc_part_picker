"""Brute force protection service for login attempts"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user import User
from ..security_config import (
    get_max_login_attempts,
    get_lockout_duration_minutes,
)


def check_account_lockout(db: Session, user: User) -> bool:
    """
    Check if an account is currently locked.
    If lockout period has expired, unlock the account.

    Returns: True if account is locked, False otherwise
    """
    if user.locked_until is None:
        return False

    now = datetime.now(timezone.utc)
    if now < user.locked_until:
        return True

    # Unlock the account
    user.locked_until = None
    user.failed_login_attempts = 0
    db.commit()
    return False


def handle_failed_login_attempt(db: Session, user: User) -> None:
    """
    Record a failed login attempt and lock account if threshold exceeded.
    """
    max_attempts = get_max_login_attempts()
    lockout_duration = get_lockout_duration_minutes()

    user.failed_login_attempts += 1

    if user.failed_login_attempts >= max_attempts:
        # Lock the account
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=lockout_duration)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked due to too many failed login attempts. Try again in {lockout_duration} minutes."
        )
    else:
        remaining_attempts = max_attempts - user.failed_login_attempts
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials. {remaining_attempts} attempts remaining before account lockout."
        )


def handle_successful_login(db: Session, user: User) -> None:
    """
    Reset failed login attempts on successful authentication.
    """
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()


def validate_login_attempt(db: Session, user: User) -> None:
    """
    Validate that a login attempt is allowed.
    Raises HTTPException if account is locked.
    """
    if check_account_lockout(db, user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account is temporarily locked due to too many failed login attempts. Please try again later."
        )
