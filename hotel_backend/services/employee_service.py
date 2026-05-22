from sqlalchemy.orm import Session
from models import Employee

def create_employee(db: Session, employee_data, hashed_password):
    try:
        new_emp = Employee(
            full_name=employee_data.full_name,
            position=employee_data.position,
            username=employee_data.username,
            hashed_password=hashed_password,
            role=employee_data.role
        )
        db.add(new_emp)
        db.commit()
        db.refresh(new_emp)
        return new_emp.id
    except Exception as e:
        db.rollback()
        print("Error creating employee:", e)
        return None

def get_employee(db: Session, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_all_employees(db: Session, skip: int = 0, limit: int = 10, search: str = None):
    query = db.query(Employee)
    if search:
        query = query.filter(
            (Employee.full_name.ilike(f"%{search}%")) |
            (Employee.username.ilike(f"%{search}%")) |
            (Employee.email.ilike(f"%{search}%") if hasattr(Employee, 'email') else None)
        )
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

def update_employee(db: Session, employee_id: int, update_data):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        return False
    
    if 'full_name' in update_data: emp.full_name = update_data['full_name']
    if 'position' in update_data: emp.position = update_data['position']
    if 'role' in update_data: emp.role = update_data['role']
    if 'username' in update_data: emp.username = update_data['username']
    
    db.commit()
    return True

def delete_employee(db: Session, employee_id: int):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        return False
    db.delete(emp)
    db.commit()
    return True