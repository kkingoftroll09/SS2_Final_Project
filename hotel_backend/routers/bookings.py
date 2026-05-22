from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import List

import services.booking_service as booking_service
from db import get_db

router = APIRouter(prefix="/api", tags=["Đặt phòng - Bookings"])

class BookingCreate(BaseModel):
    guest_id: int
    check_in_date: date
    check_out_date: date
    room_ids: List[int] = Field(
        ..., 
        min_items=1, 
        description="Danh sách ID phòng muốn đặt"
    )
    number_of_guests: int = Field(1, ge=1, description="Số lượng khách")

    @field_validator('check_out_date')
    @classmethod
    def check_out_after_check_in(cls, v, info):
        if 'check_in_date' in info.data and v <= info.data.get('check_in_date'):
            raise ValueError('Ngày check-out phải sau ngày check-in')
        return v

class BookingUpdate(BaseModel):
    guest_id: int = None
    check_in_date: date = None
    check_out_date: date = None
    status: str = None
    number_of_guests: int = None


@router.post("/bookings", 
             status_code=status.HTTP_201_CREATED,
             summary="Tạo đặt phòng mới",
             description="Tạo booking và gán một hoặc nhiều phòng")
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    result = booking_service.create_booking(db, booking)
    if not result:
        raise HTTPException(status_code=400, detail="Không thể tạo booking: Phòng không khả dụng hoặc khách hàng không tồn tại")
    return result

@router.get("/bookings", summary="Lấy danh sách tất cả booking")
async def get_all_bookings(db: Session = Depends(get_db)):
    return booking_service.get_all_bookings(db)

@router.get("/bookings/{booking_id}", summary="Lấy thông tin chi tiết booking")
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = booking_service.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy booking")
    return booking


@router.put("/bookings/{booking_id}/status", summary="Cập nhật trạng thái booking")
async def update_booking_status(booking_id: int, status_name: str, db: Session = Depends(get_db)):
    success = booking_service.update_status(db, booking_id, status_name)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy booking")
    return {"message": f"Đã cập nhật trạng thái booking thành: {status_name}"}

@router.put("/bookings/{booking_id}", summary="Cập nhật thông tin booking")
async def update_booking(booking_id: int, update_data: BookingUpdate, db: Session = Depends(get_db)):
    data = {k: v for k, v in update_data.model_dump().items() if v is not None}
    success = booking_service.update_booking(db, booking_id, data)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy booking")
    return {"message": "Cập nhật booking thành công"}

@router.delete("/bookings/{booking_id}", summary="Xóa booking")
async def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    success = booking_service.delete_booking(db, booking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy booking")
    return {"message": "Xóa booking thành công"}