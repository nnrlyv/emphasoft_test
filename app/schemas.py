import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr,Field


class HotelRoom(BaseModel):

    room_number: int
    room_name: str
    room_price: int
    number_of_places: int
    type_of_room: str
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None


class BookingRequest(BaseModel):
    room_number: int
    check_in_date: date
    check_out_date: date


class RoomCreate(BaseModel):
    room_number: int
    room_name: str
    room_price: int
    number_of_places: int
    type_of_room: str


class BookingUpdate(BaseModel):
    check_in_date: date
    check_out_date: date


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
