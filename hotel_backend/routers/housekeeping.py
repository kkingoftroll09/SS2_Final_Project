from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from db import get_db
import services.housekeeping_service as housekeeping_service
import services.auth_service as auth_service
from models import Employee, Room

router = APIRouter(prefix="/housekeeping")

class TaskCreate(BaseModel):
    room_id: int
    employee_id: int
    notes: Optional[str] = None

class TaskStatusUpdate(BaseModel):
    status: str

@router.post("/tasks")
async def create_task(
    task: TaskCreate, 
    current_user: Employee = Depends(auth_service.require_role(["admin", "receptionist"])),
    db: Session = Depends(get_db)
):
    task_id = housekeeping_service.create_task(db, task.room_id, task.employee_id, task.notes)
    # Also update the room status to 'needs_cleaning' when a task is created
    room = db.query(Room).filter(Room.id == task.room_id).first()
    if room:
        room.status = 'needs_cleaning'
        db.commit()
    
    return {"id": task_id, "message": "Task created successfully"}

@router.get("/tasks")
async def get_tasks(
    status: Optional[str] = None, 
    employee_id: Optional[int] = None,
    current_user: Employee = Depends(auth_service.get_current_active_employee),
    db: Session = Depends(get_db)
):
    # If role is housekeeping, they can only see their own tasks
    if current_user.role == "housekeeping":
        employee_id = current_user.id
        
    return housekeeping_service.get_tasks(db, status, employee_id)

@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: int, 
    update: TaskStatusUpdate,
    current_user: Employee = Depends(auth_service.get_current_active_employee),
    db: Session = Depends(get_db)
):
    success = housekeeping_service.update_task_status(db, task_id, update.status)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task status updated"}
