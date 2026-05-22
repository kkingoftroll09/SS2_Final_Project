from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.orm import Session
from db import get_db
import services.guest_service as guest_service

router = APIRouter(prefix="/api", tags=["Khách hàng - Guests"])

class GuestCreate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    phone: str = Field(..., min_length=9, max_length=20)
    address: str | None = None

class GuestUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=3, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(None, min_length=9, max_length=20)
    address: str | None = None

class GuestResponse(GuestCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

@router.post("/guests", status_code=status.HTTP_201_CREATED,
             summary="Tạo khách hàng mới")
async def create_guest(guest: GuestCreate, db: Session = Depends(get_db)):
    guest_id = guest_service.create_guest(db, guest)
    if not guest_id:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    return {"id": guest_id, **guest.model_dump()}

@router.get("/guests", summary="Lấy danh sách khách hàng")
async def list_guests(skip: int = Query(0), limit: int = Query(10), search: str = Query(None), db: Session = Depends(get_db)):
    result = guest_service.get_all_guests(db, skip=skip, limit=limit, search=search)
    return {
        "items": [{"guest_id": g.id, "full_name": g.full_name, "email": g.email, "phone": g.phone, "address": g.address} for g in result["items"]],
        "total": result["total"]
    }

@router.get("/guests/{guest_id}", summary="Lấy thông tin khách hàng", response_model=GuestResponse)
async def get_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = guest_service.get_guest(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    return guest

@router.put("/guests/{guest_id}", summary="Cập nhật thông tin khách hàng")
async def update_guest(guest_id: int, guest: GuestUpdate, db: Session = Depends(get_db)):
    success = guest_service.update_guest(db, guest_id, guest)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    return {"message": "Cập nhật khách hàng thành công"}

@router.delete("/guests/{guest_id}", summary="Xóa khách hàng")
async def delete_guest(guest_id: int, db: Session = Depends(get_db)):
    success = guest_service.delete_guest(db, guest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    return {"message": "Xóa khách hàng thành công"}