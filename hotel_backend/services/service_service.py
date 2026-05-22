from sqlalchemy.orm import Session
from models import Service

def get_all_services(db: Session, skip: int = 0, limit: int = 10, search: str = None):
    query = db.query(Service)
    if search:
        query = query.filter(Service.name.ilike(f"%{search}%"))
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {
        "items": [{"service_id": s.id, "service_name": s.name, "service_price": float(s.price), "description": getattr(s, 'description', '')} for s in items],
        "total": total
    }

def get_service(db: Session, service_id: int):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return None
    return {"service_id": service.id, "service_name": service.name, "service_price": float(service.price), "description": getattr(service, 'description', '')}

def create_service(db: Session, service_data):
    try:
        new_service = Service(
            name=service_data.get('service_name'),
            price=service_data.get('service_price'),
            description=service_data.get('description')
        )
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
        return get_service(db, new_service.id)
    except Exception as e:
        db.rollback()
        return None

def update_service(db: Session, service_id: int, service_data):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return False
    
    if 'service_name' in service_data: service.name = service_data['service_name']
    if 'service_price' in service_data: service.price = service_data['service_price']
    if 'description' in service_data: service.description = service_data['description']
    
    db.commit()
    return True

def delete_service(db: Session, service_id: int):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return False
    db.delete(service)
    db.commit()
    return True
