from sqlalchemy.orm import Session
from models import Guest

def create_guest(db: Session, guest_data):
    existing = db.query(Guest).filter(Guest.email == guest_data.email).first()
    if existing:
        return existing.id
    new_guest = Guest(
        full_name=guest_data.full_name,
        email=guest_data.email,
        phone=guest_data.phone,
        address=guest_data.address
    )
    db.add(new_guest)
    db.commit()
    db.refresh(new_guest)
    return new_guest.id

def get_guest(db: Session, guest_id: int):
    return db.query(Guest).filter(Guest.id == guest_id).first()

def update_guest(db: Session, guest_id: int, guest_data):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        return False
    
    if guest_data.full_name is not None: guest.full_name = guest_data.full_name
    if guest_data.email is not None:     guest.email = guest_data.email
    if guest_data.phone is not None:     guest.phone = guest_data.phone
    if guest_data.address is not None:   guest.address = guest_data.address

    db.commit()
    return True

def delete_guest(db: Session, guest_id: int):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        return False
    db.delete(guest)
    db.commit()
    return True

def get_all_guests(db: Session, skip: int = 0, limit: int = 10, search: str = None):
    query = db.query(Guest)
    if search:
        query = query.filter(
            (Guest.full_name.ilike(f"%{search}%")) |
            (Guest.email.ilike(f"%{search}%")) |
            (Guest.phone.ilike(f"%{search}%"))
        )
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}