import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def _normalize_password(password: str) -> str:
    """
    Приводим пароль к фиксированной длине (bcrypt ≤ 72 bytes)
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    normalized = _normalize_password(password)
    return pwd_context.hash(normalized)

def verify_password(password: str, hashed_password: str) -> bool:
    normalized = _normalize_password(password)
    return pwd_context.verify(normalized, hashed_password)
