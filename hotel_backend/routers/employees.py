from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from db import get_db
import services.employee_service as employee_service
import services.auth_service as auth_service
from models import Employee

router = APIRouter()

class EmployeeCreate(BaseModel):
    full_name: str
    position: str
    username: str
    password: str
    role: str = "receptionist"

class EmployeeResponse(BaseModel):
    id: int
    full_name: str
    position: str
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)

class EmployeeUpdate(BaseModel):
    full_name: str = None
    position: str = None
    role: str = None
    username: str = None

@router.post("/employees", response_model=EmployeeResponse)
async def create_employee(
    employee: EmployeeCreate,
    current_user: Employee = Depends(auth_service.require_role(["admin"])),
    db: Session = Depends(get_db)
):
    hashed_password = auth_service.get_password_hash(employee.password)
    employee_id = employee_service.create_employee(db, employee, hashed_password)
    if not employee_id:
        raise HTTPException(400, "Could not create employee (username might exist)")
    return {
        "id": employee_id, 
        "username": employee.username, 
        "full_name": employee.full_name, 
        "position": employee.position,
        "role": employee.role
    }

@router.get("/employees")
async def list_employees(
    skip: int = Query(0),
    limit: int = Query(10),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    result = employee_service.get_all_employees(db, skip=skip, limit=limit, search=search)
    return {
        "items": [{"employee_id": e.id, "name": e.full_name, "phone": getattr(e, 'phone', ''), "email": getattr(e, 'email', ''), "role": e.role} for e in result["items"]],
        "total": result["total"]
    }

@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    current_user: Employee = Depends(auth_service.get_current_active_employee),
    db: Session = Depends(get_db)
):
    employee = employee_service.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(404, "Employee not found")
    # Ensure response fields match the response model and avoid None values
    return {
        "id": int(employee.id),
        "username": employee.username or "",
        "full_name": employee.full_name or "",
        "position": employee.position or "",
        "role": employee.role or "",
    }

@router.put("/employees/{employee_id}")
async def update_employee(
    employee_id: int,
    update_data: EmployeeUpdate,
    current_user: Employee = Depends(auth_service.require_role(["admin"])),
    db: Session = Depends(get_db)
):
    data = {k: v for k, v in update_data.model_dump().items() if v is not None}
    success = employee_service.update_employee(db, employee_id, data)
    if not success:
        raise HTTPException(404, "Employee not found")
    return {"message": "Employee updated"}

@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: int,
    current_user: Employee = Depends(auth_service.require_role(["admin"])),
    db: Session = Depends(get_db)
):
    success = employee_service.delete_employee(db, employee_id)
    if not success:
        raise HTTPException(404, "Employee not found")
    return {"message": "Employee deleted"}