import uuid
from sqlalchemy import Column, String, DateTime, Integer, Date, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.db.session_db import Base


class UserModel(Base):
    __tablename__ = "users"

    uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.now)
    is_admin = Column(Boolean, default=True)

class HotelRoomModel(Base):
    __tablename__ = "rooms"

    room_uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_number = Column(Integer, unique=True, nullable=False)
    room_name = Column(String, nullable=False)
    room_price = Column(Integer, nullable=False)
    number_of_places = Column(Integer, nullable=False)
    type_of_room = Column(String, nullable=False)

    check_in_date = Column(Date, nullable=True)
    check_out_date = Column(Date, nullable=True)


class BookingModel(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room_uid = Column(UUID(as_uuid=True), ForeignKey("rooms.room_uid"))
    room_number = Column(Integer, nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uid"), nullable=False)

