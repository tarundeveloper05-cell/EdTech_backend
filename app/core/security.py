from app.services.auth_service import AuthService


def hash_password(password: str) -> str:
    return AuthService.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return AuthService.verify_password(plain_password, hashed_password)
