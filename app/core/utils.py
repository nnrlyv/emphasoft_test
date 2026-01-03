import uuid
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException
from app.core.config import config  # твоё окружение с JWT_SECRET и JWT_ALGORITHM


def create_access_token(user_uid: uuid.UUID, user_data: dict, expiry: timedelta = None) -> str:
    
    payload = {
        "sub": str(user_uid),
        "user": user_data,
        "exp": datetime.now() + (expiry if expiry else timedelta(minutes=60))
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
