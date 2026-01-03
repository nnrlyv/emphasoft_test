from app.db.session_db import get_db
from app.db.models_db import UserModel
from app.core.security_password import hash_password

db = next(get_db())


admin_user = UserModel(
    email="admin@example.com",
    hashed_password=hash_password("stringst"),
    is_admin=True
)

db.add(admin_user)
db.commit()
db.refresh(admin_user)

print("Admin создан с uid:", admin_user.uid)
