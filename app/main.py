from fastapi import FastAPI

from app.api.routes import room_router, admin_router, both_router
from app.api.auth import auth_router
from app.db.session_db import Base, engine

app= FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(room_router, tags=["Room related"])
app.include_router(admin_router, tags=["Admin Only"])
app.include_router(both_router, tags=["For Both: User and Admin"])
app.include_router(auth_router, tags=["Authentication"])


