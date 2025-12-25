from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session_db import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.db.models_db import HotelRoomModel, BookingModel, UserModel
from app.schemas import HotelRoom, BookingRequest, RoomCreate, BookingUpdate

room_router = APIRouter()
admin_router = APIRouter()
both_router = APIRouter()



@room_router.get("/rooms", response_model=List[HotelRoom])
def get_rooms(
    price: Optional[int] = Query(None, description="Цена комнаты"),
    number_of_places: Optional[int] = Query(None, description="Количество мест"),
    sort_by_price: Optional[bool] = Query(False, description="Сортировка по цене"),
    db: Session = Depends(get_db)
):
    query = db.query(HotelRoomModel)

    if price is not None:
        query = query.filter(HotelRoomModel.room_price <= price)
    if number_of_places is not None:
        query = query.filter(HotelRoomModel.number_of_places == number_of_places)
    if sort_by_price:
        query = query.order_by(HotelRoomModel.room_price)

    return query.all()


def is_room_free(room_number: int, check_in: date, check_out: date, db: Session):
    conflict = db.query(BookingModel).filter(
        BookingModel.room_number == room_number,
        BookingModel.check_in_date < check_out,
        BookingModel.check_out_date > check_in
    ).first()
    return conflict is None


@room_router.get("/available_rooms", response_model=List[HotelRoom])
def get_available_rooms(
    check_in: date = Query(...),
    check_out: date = Query(...),
    db: Session = Depends(get_db)
):
    rooms = db.query(HotelRoomModel).all()
    available_rooms = [
        room for room in rooms
        if is_room_free(room.room_number, check_in, check_out, db)
    ]
    return available_rooms


@room_router.post("/book_room")
def book_room(
    room_data: BookingRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(HotelRoomModel).filter(HotelRoomModel.room_number == room_data.room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not is_room_free(room_data.room_number, room_data.check_in_date, room_data.check_out_date, db):
        raise HTTPException(status_code=400, detail="Room is not available for these dates")

    booking = BookingModel(
        room_number=room_data.room_number,
        check_in_date=room_data.check_in_date,
        check_out_date=room_data.check_out_date,
        user_id=user.uid
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {
        "msg": "Room successfully booked",
        "booking_id": booking.id,
        "room_number": booking.room_number,
        "check_in_date": booking.check_in_date,
        "check_out_date": booking.check_out_date
    }




@admin_router.post("/admin/rooms")
def create_room(room: RoomCreate, admin: UserModel = Depends(get_current_admin),db: Session = Depends(get_db)):
    if db.query(HotelRoomModel).filter(HotelRoomModel.room_number == room.room_number).first():
        raise HTTPException(status_code=400, detail="Room already exists")

    db_room = HotelRoomModel(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return {"message": "Room created successfully", "room_uid": db_room.room_uid}


@admin_router.put("/admin/rooms/{room_number}")
def update_room(room_number: int, data: RoomCreate,admin: UserModel = Depends(get_current_admin), db: Session = Depends(get_db)):
    room = db.query(HotelRoomModel).filter(HotelRoomModel.room_number == room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    for key, value in data.model_dump().items():
        setattr(room, key, value)

    db.commit()
    db.refresh(room)
    return {"message": "Room updated", "room_id": room.room_uid}


@admin_router.delete("/admin/rooms/{room_number}")
def delete_room(room_number: int,admin: UserModel = Depends(get_current_admin), db: Session = Depends(get_db)):
    room = db.query(HotelRoomModel).filter(HotelRoomModel.room_number == room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Удаляем связанные бронирования
    db.query(BookingModel).filter(BookingModel.room_number == room_number).delete()
    db.delete(room)
    db.commit()
    return {"message": "Room and related bookings deleted"}


@admin_router.put("/admin/bookings/{booking_id}")
def update_booking(booking_id: int, data: BookingUpdate,admin: UserModel = Depends(get_current_admin), db: Session = Depends(get_db)):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.check_in_date = data.check_in_date
    booking.check_out_date = data.check_out_date
    db.commit()
    db.refresh(booking)
    return {"message": "Booking updated", "booking_id": booking.id}


@both_router.delete("/admin/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    db.delete(booking)
    db.commit()
    return {"message": "Booking canceled", "booking_id": booking.id}
