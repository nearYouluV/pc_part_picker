from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    refresh_token = Column(Text, nullable=True)  # Store current refresh token
    refresh_token_expires = Column(DateTime(timezone=True), nullable=True)  # Refresh token expiry
    # Brute force protection fields
    failed_login_attempts = Column(Integer, default=0, nullable=False)  # Track consecutive failed attempts
    locked_until = Column(DateTime(timezone=True), nullable=True)  # Account locked until this time
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
