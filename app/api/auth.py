import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas import UserRegister, UserLogin, Token
from app.db.models_db import UserModel
from app.core.security_password import hash_password, verify_password
from app.core.utils import create_access_token
from app.db.session_db import get_db

auth_router = APIRouter()


@auth_router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    # Проверяем, есть ли уже такой email
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Создаём нового пользователя
    db_user = UserModel(
        uid=uuid.uuid4(),
        email=user.email,
        password=hash_password(user.password),
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User registered successfully", "user_uid": db_user.uid}


@auth_router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Ищем пользователя в базе
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Генерируем JWT токен
    token = create_access_token(
        user_uid=db_user.uid,
        user_data={"email": db_user.email, "role": db_user.role}
    )

    return {"access_token": token, "token_type": "bearer"}
