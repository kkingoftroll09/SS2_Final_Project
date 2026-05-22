import db

def get_all_services():
    return db.fetch_all("SELECT id, name, price FROM service")

def add_service(booking_detail_id: int, service_id: int, employee_id: int, quantity: int = 1):
    # Validate inputs
    if quantity is None or int(quantity) <= 0:
        return None

    svc = db.fetch_one("SELECT price FROM service WHERE id = %s", (service_id,))
    if not svc:
        return None
    emp = db.fetch_one("SELECT id FROM employee WHERE id = %s", (employee_id,))
    if not emp:
        return None

    bd = db.fetch_one("SELECT id FROM booking_detail WHERE id = %s", (booking_detail_id,))
    if not bd:
        return None
    total = svc['price'] * quantity

    return db.execute_query("""
        INSERT INTO booking_service 
        (booking_detail_id, service_id, employee_id, quantity, total_price)
        VALUES (%s, %s, %s, %s, %s)
    """, (booking_detail_id, service_id, employee_id, quantity, total))

def get_services_for_room(booking_detail_id: int):
    return db.fetch_all("""
        SELECT bs.*, s.name as service_name, e.full_name as employee_name
        FROM booking_service bs
        JOIN service s ON bs.service_id = s.id
        JOIN employee e ON bs.employee_id = e.id
        WHERE bs.booking_detail_id = %s
    """, (booking_detail_id,))