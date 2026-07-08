import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt
from jose import jwt
from jose.exceptions import JWTError


class AuthService:
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except ValueError:
            return False

    @classmethod
    def create_access_token(
        cls,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta
            if expires_delta is not None
            else timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM]
            )
            return payload
        except JWTError:
          return None