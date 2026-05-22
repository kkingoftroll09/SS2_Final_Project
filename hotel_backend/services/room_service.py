from sqlalchemy.orm import Session
from sqlalchemy import text
from models import RoomType, Room

def get_all_room_types(db: Session):
    types = db.query(RoomType).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "base_price": float(t.base_price),
            "max_occupancy": t.max_occupancy,
        }
        for t in types
    ]

def get_rooms(db: Session, status=None, check_in_date=None, check_out_date=None):
    query = """
        SELECT
            r.id AS room_id,
            r.room_number,
            r.floor,
            r.room_type_id,
            rt.name AS type_name,
            rt.base_price,
            rt.max_occupancy,
            r.status
        FROM room r JOIN room_type rt ON r.room_type_id = rt.id
    """
    params = {}

    if status:
        query += " WHERE r.status = :status"
        params['status'] = status

    if check_in_date and check_out_date:
        if status:
            query += " AND"
        else:
            query += " WHERE"
        query += """
            NOT EXISTS (
                SELECT 1 FROM booking_detail bd
                JOIN booking b ON bd.booking_id = b.id
                WHERE bd.room_id = r.id
                AND b.status != 'cancelled'
                AND b.check_in_date < :co AND b.check_out_date > :ci
            )
        """
        params['ci'] = check_in_date
        params['co'] = check_out_date

    results = db.execute(text(query), params).mappings().all()
    items = []
    for row in results:
        item = dict(row)
        if item.get("base_price") is not None:
            item["base_price"] = float(item["base_price"])
        item["room_type"] = item.get("type_name")
        items.append(item)
    return items

def get_room(db: Session, room_id: int):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        return None
    return {
        "room_id": room.id,
        "id": room.id,
        "room_number": room.room_number,
        "room_type_id": room.room_type_id,
        "type_name": room.room_type.name if room.room_type else None,
        "room_type": room.room_type.name if room.room_type else None,
        "status": room.status,
        "floor": getattr(room, 'floor', None),
        "base_price": float(room.room_type.base_price) if room.room_type else 0,
        "max_occupancy": room.room_type.max_occupancy if room.room_type else None,
    }

def create_room(db: Session, room_data):
    try:
        new_room = Room(
            room_number=room_data.room_number,
            room_type_id=room_data.room_type_id,
            status=room_data.get('status', 'available'),
            floor=room_data.get('floor')
        )
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        return get_room(db, new_room.id)
    except Exception as e:
        db.rollback()
        return None

def update_room(db: Session, room_id: int, room_data):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        return False
    
    if 'room_number' in room_data: room.room_number = room_data['room_number']
    if 'room_type_id' in room_data: room.room_type_id = room_data['room_type_id']
    if 'status' in room_data: room.status = room_data['status']
    if 'floor' in room_data: room.floor = room_data['floor']
    
    db.commit()
    return True

def delete_room(db: Session, room_id: int):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        return False
    db.delete(room)
    db.commit()
    return True