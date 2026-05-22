from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date
from db import get_db
import services.room_service as room_service

router = APIRouter()

class RoomStatusUpdate(BaseModel):
    status: str

class RoomCreate(BaseModel):
    room_number: str
    room_type_id: int
    status: str = "available"
    floor: int = None

class RoomUpdate(BaseModel):
    room_number: str = None
    room_type_id: int = None
    status: str = None
    floor: int = None

@router.get("/rooms")
async def get_rooms(
    status: str = Query(None),
    check_in_date: date = Query(None),
    check_out_date: date = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    items = room_service.get_rooms(db, status, check_in_date, check_out_date)
    return {"items": items[skip:skip+limit], "total": len(items)}

@router.post("/rooms", status_code=201)
async def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    result = room_service.create_room(db, room.model_dump())
    if not result:
        raise HTTPException(400, "Could not create room (may be duplicate)")
    return result

@router.get("/rooms/{room_id}")
async def get_room(room_id: int, db: Session = Depends(get_db)):
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    return room

@router.put("/rooms/{room_id}")
async def update_room(room_id: int, update_data: RoomUpdate, db: Session = Depends(get_db)):
    data = {k: v for k, v in update_data.model_dump().items() if v is not None}
    success = room_service.update_room(db, room_id, data)
    if not success:
        raise HTTPException(404, "Room not found")
    return {"message": "Room updated"}

@router.delete("/rooms/{room_id}")
async def delete_room(room_id: int, db: Session = Depends(get_db)):
    success = room_service.delete_room(db, room_id)
    if not success:
        raise HTTPException(404, "Room not found")
    return {"message": "Room deleted"}

@router.put("/rooms/{room_number}/status")
async def update_room_status(room_number: str, update: RoomStatusUpdate, db: Session = Depends(get_db)):
    success = room_service.update_room_status(db, room_number, update.status)
    if not success:
        raise HTTPException(404, "Room not found")
    return {"message": f"Room {room_number} status updated"}