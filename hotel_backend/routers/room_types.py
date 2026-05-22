from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
import services.room_service as room_service

router = APIRouter()

@router.get("/room-types", summary="Lấy danh sách loại phòng")
async def get_room_types(db: Session = Depends(get_db)):
    return room_service.get_all_room_types(db)