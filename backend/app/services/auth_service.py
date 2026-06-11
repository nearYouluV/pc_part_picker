from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import hmac
from uuid import uuid4
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..models.user import User
from ..auth_schemas import TokenData
from ..database import get_db
import os


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_ISSUER = os.getenv("JWT_ISSUER", "analytics_tool")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "analytics_tool_clients")


security = HTTPBearer()


def normalize_email(email: Optional[str]) -> Optional[str]:
    if email is None:
        return None
    return email.strip().lower()


def normalize_username(username: Optional[str]) -> Optional[str]:
    if username is None:
        return None
    return username.strip().lower()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    to_encode["token_type"] = "access"
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": str(uuid4()),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["token_type"] = "refresh"
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": str(uuid4()),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_refresh_token(refresh_token: str) -> str:
    token_bytes = refresh_token.encode("utf-8")
    key_bytes = SECRET_KEY.encode("utf-8")
    return hmac.new(key_bytes, token_bytes, hashlib.sha256).hexdigest()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    normalized_username = normalize_username(username)
    if normalized_username is None:
        return None
    return db.query(User).filter(func.lower(User.username) == normalized_username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    normalized_email = normalize_email(email)
    if normalized_email is None:
        return None
    return db.query(User).filter(func.lower(User.email) == normalized_email).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, username: str, password: str, email: Optional[str] = None) -> User:
    hashed_password = get_password_hash(password)
    normalized_email = normalize_email(email)
    normalized_username = normalize_username(username)
    user = User(
        email=normalized_email,
        username=normalized_username,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_refresh_token(db: Session, refresh_token: str) -> Optional[User]:
    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("token_type")

        if token_type != "refresh":
            return None

        if user_id is None:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if user is None or user.refresh_token is None:
            return None

        hashed_token = hash_refresh_token(refresh_token)
        if not hmac.compare_digest(user.refresh_token, hashed_token):
            # Backward compatibility for old plaintext refresh tokens.
            if not hmac.compare_digest(user.refresh_token, refresh_token):
                return None
            user.refresh_token = hashed_token
            db.commit()

        if user.refresh_token_expires and user.refresh_token_expires < datetime.now(timezone.utc):
            return None

        return user
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
        user_id: int = payload.get("user_id")
        username: str = payload.get("sub")
        token_type: str = payload.get("token_type")

        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if username is None or user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id, username=username, token_type=token_type)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
