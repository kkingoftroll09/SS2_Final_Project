from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from fastapi import Depends
import services.service_service as service_service

router = APIRouter()

class ServiceCreate(BaseModel):
    service_name: str
    service_price: float
    description: str = None

class ServiceUpdate(BaseModel):
    service_name: str = None
    service_price: float = None
    description: str = None

@router.get("/services", summary="Lấy danh sách dịch vụ")
async def get_services(skip: int = Query(0), limit: int = Query(10), search: str = Query(None), db: Session = Depends(get_db)):
    return service_service.get_all_services(db, skip=skip, limit=limit, search=search)

@router.post("/services", status_code=201, summary="Tạo dịch vụ mới")
async def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    result = service_service.create_service(db, service.model_dump())
    if not result:
        raise HTTPException(400, "Could not create service")
    return result

@router.get("/services/{service_id}", summary="Lấy thông tin dịch vụ")
async def get_service(service_id: int, db: Session = Depends(get_db)):
    service = service_service.get_service(db, service_id)
    if not service:
        raise HTTPException(404, "Service not found")
    return service

@router.put("/services/{service_id}", summary="Cập nhật dịch vụ")
async def update_service(service_id: int, update_data: ServiceUpdate, db: Session = Depends(get_db)):
    data = {k: v for k, v in update_data.model_dump().items() if v is not None}
    success = service_service.update_service(db, service_id, data)
    if not success:
        raise HTTPException(404, "Service not found")
    return {"message": "Service updated"}

@router.delete("/services/{service_id}", summary="Xóa dịch vụ")
async def delete_service(service_id: int, db: Session = Depends(get_db)):
    success = service_service.delete_service(db, service_id)
    if not success:
        raise HTTPException(404, "Service not found")
    return {"message": "Service deleted"}