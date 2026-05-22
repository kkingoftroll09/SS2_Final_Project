from sqlalchemy.orm import Session
from models import HousekeepingTask, Room

def create_task(db: Session, room_id: int, employee_id: int, notes: str = None):
    new_task = HousekeepingTask(room_id=room_id, employee_id=employee_id, notes=notes, status='TODO')
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task.id

def get_tasks(db: Session, status: str = None, employee_id: int = None):
    query = db.query(HousekeepingTask)
    if status:
        query = query.filter(HousekeepingTask.status == status)
    if employee_id:
        query = query.filter(HousekeepingTask.employee_id == employee_id)
        
    tasks = query.all()
    return [{
        "id": t.id,
        "room_id": t.room_id,
        "employee_id": t.employee_id,
        "status": t.status,
        "notes": t.notes,
        "created_at": t.created_at,
        "updated_at": t.updated_at,
        "room_number": t.room.room_number if t.room else None,
        "employee_name": t.employee.full_name if t.employee else None
    } for t in tasks]

def get_task(db: Session, task_id: int):
    return db.query(HousekeepingTask).filter(HousekeepingTask.id == task_id).first()

def update_task_status(db: Session, task_id: int, new_status: str):
    task = get_task(db, task_id)
    if not task:
        return False
        
    task.status = new_status
    
    if new_status == "DONE" and task.room:
        # The room is now clean and available
        task.room.status = 'available'
        
    db.commit()
    return True
