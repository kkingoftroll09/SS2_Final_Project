from sqlalchemy import text, inspect
from db import SessionLocal, engine, Base
from models import (
    Employee,
    RoomType,
    Room,
    Guest,
    Booking,
    BookingDetail,
    Payment,
    Service,
    HousekeepingTask,
)
from services.auth_service import get_password_hash

# Create tables if they don't exist (needed when falling back to SQLite)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print('Warning: could not create tables automatically:', e)


def ensure_employee_auth_columns(db):
    """Backfill auth columns for legacy employee schema before seeding."""
    inspector = inspect(engine)
    existing_columns = {col["name"] for col in inspector.get_columns("employee")}

    if "username" not in existing_columns:
        db.execute(text("ALTER TABLE employee ADD COLUMN username VARCHAR(50)"))
    if "hashed_password" not in existing_columns:
        db.execute(text("ALTER TABLE employee ADD COLUMN hashed_password VARCHAR(255)"))
    if "role" not in existing_columns:
        db.execute(text("ALTER TABLE employee ADD COLUMN role VARCHAR(20)"))

    db.commit()

def ensure_room_columns_and_backfill(db):
    """Ensure room data columns exist and backfill missing values for dashboard/table display."""
    inspector = inspect(engine)

    room_columns = {col["name"] for col in inspector.get_columns("room")}
    room_type_columns = {col["name"] for col in inspector.get_columns("room_type")}

    if "floor" not in room_columns:
        db.execute(text("ALTER TABLE room ADD COLUMN floor INT NULL"))

    if "max_occupancy" not in room_type_columns:
        db.execute(text("ALTER TABLE room_type ADD COLUMN max_occupancy INT NULL"))

    # Backfill floor from room number first digit(s), e.g. 301 -> 3.
    db.execute(text("""
        UPDATE room
                SET floor = CAST(SUBSTRING(room_number FROM 1 FOR 1) AS INTEGER)
        WHERE floor IS NULL
                    AND room_number ~ '^[0-9]'
    """))

    # Fill sensible occupancy defaults by type name.
    db.execute(text("""
        UPDATE room_type
        SET max_occupancy = CASE
            WHEN LOWER(name) LIKE '%suite%' THEN 4
            WHEN LOWER(name) LIKE '%deluxe%' THEN 3
            WHEN LOWER(name) LIKE '%standard%' THEN 2
            ELSE 2
        END
        WHERE max_occupancy IS NULL
    """))

    db.commit()

def seed_database():
    db = SessionLocal()
    
    try:
        print("Starting database seed...")
        ensure_employee_auth_columns(db)
        ensure_room_columns_and_backfill(db)
        
        # ==============================================================
        # 1. Seed Employees (Roles for testing)
        # ==============================================================
        employees_data = [
            {"username": "admin", "password": "password123", "full_name": "System Admin", "position": "IT", "role": "admin"},
            {"username": "manager", "password": "password123", "full_name": "Alice Manager", "position": "Hotel Manager", "role": "manager"},
            {"username": "receptionist", "password": "password123", "full_name": "Bob Reception", "position": "Front Desk", "role": "receptionist"},
            {"username": "cleaner", "password": "password123", "full_name": "Charlie Clean", "position": "Housekeeper", "role": "housekeeping"},
            {"username": "waiter", "password": "password123", "full_name": "Dave Waiter", "position": "Restaurant Waiter", "role": "waiter"},
        ]
        
        print("Seeding Employees...")
        for emp_data in employees_data:
            existing = db.query(Employee).filter(Employee.username == emp_data["username"]).first()
            password_hash = get_password_hash(emp_data["password"])
            if not existing:
                emp = Employee(
                    username=emp_data["username"],
                    hashed_password=password_hash,
                    full_name=emp_data["full_name"],
                    position=emp_data["position"],
                    role=emp_data["role"]
                )
                db.add(emp)
            else:
                existing.hashed_password = password_hash
                existing.full_name = emp_data["full_name"]
                existing.position = emp_data["position"]
                existing.role = emp_data["role"]
        db.commit()

        # ==============================================================
        # 2. Seed Room Types & Rooms
        # ==============================================================
        print("Seeding Room Types & Rooms...")
        standard_type = db.query(RoomType).filter(RoomType.name == "Standard").first()
        if not standard_type:
            standard_type = RoomType(name="Standard", base_price=50.00, max_occupancy=2)
            deluxe_type = RoomType(name="Deluxe", base_price=100.00, max_occupancy=3)
            suite_type = RoomType(name="Suite", base_price=200.00, max_occupancy=4)
            db.add_all([standard_type, deluxe_type, suite_type])
            db.commit()
            
            # Create rooms
            rooms = [
                Room(room_number="101", room_type_id=standard_type.id, status="available", floor=1),
                Room(room_number="102", room_type_id=standard_type.id, status="needs_cleaning", floor=1),
                Room(room_number="201", room_type_id=deluxe_type.id, status="occupied", floor=2),
                Room(room_number="301", room_type_id=suite_type.id, status="available", floor=3),
            ]
            db.add_all(rooms)
            db.commit()

        # ==============================================================
        # 3. Seed Services (Using raw SQL since there's no Service model yet)
        # ==============================================================
        print("Seeding Services...")
        existing_services = db.execute(text("SELECT id FROM service LIMIT 1")).fetchone()
        if not existing_services:
            db.execute(text("""
                INSERT INTO service (name, price) VALUES 
                ('Spa Massage', 50.00),
                ('Room Service Burger', 15.00),
                ('Laundry', 10.00)
            """))
            db.commit()

        # ==============================================================
        # 4. Seed Sample Guests, Booking, Payment, BookingService, Housekeeping
        # ==============================================================
        print("Seeding sample guests and a booking...")
        sample_guests = [
            {"full_name": "John Doe", "email": "john.doe@example.com", "phone": "555-0101", "address": "123 Main St"},
            {"full_name": "Jane Smith", "email": "jane.smith@example.com", "phone": "555-0202", "address": "456 Oak Ave"},
        ]
        for g in sample_guests:
            existing_g = db.query(Guest).filter(Guest.email == g["email"]).first()
            if not existing_g:
                db.add(Guest(**g))
        db.commit()

        # Choose an available room
        room = db.query(Room).filter(Room.status == 'available').first()
        if not room:
            room = db.query(Room).first()

        if room:
            guest = db.query(Guest).filter(Guest.email == 'john.doe@example.com').first()
            if guest:
                from datetime import date, timedelta

                check_in = date.today() + timedelta(days=1)
                check_out = check_in + timedelta(days=2)

                # avoid duplicate booking for same guest/dates
                exists_booking = db.query(Booking).filter(
                    Booking.guest_id == guest.id,
                    Booking.check_in_date == check_in,
                    Booking.check_out_date == check_out,
                ).first()

                if not exists_booking:
                    booking = Booking(
                        guest_id=guest.id,
                        check_in_date=check_in,
                        check_out_date=check_out,
                        status='confirmed',
                        number_of_guests=2,
                    )
                    db.add(booking)
                    db.commit()

                    # price per night from room_type if available
                    price = None
                    if room and getattr(room, 'room_type', None) and getattr(room.room_type, 'base_price', None) is not None:
                        price = float(room.room_type.base_price)
                    else:
                        price = 75.0

                    detail = BookingDetail(booking_id=booking.id, room_id=room.id, price_per_night=price)
                    db.add(detail)
                    db.commit()

                    nights = (check_out - check_in).days
                    total = price * nights
                    payment_amount = round(total * 0.5, 2)
                    payment = Payment(booking_id=booking.id, amount=payment_amount, payment_method='card')
                    db.add(payment)
                    db.commit()

                    # attach a spa service if available
                    svc = db.query(Service).filter(Service.name.ilike('%spa%')).first()
                    if svc:
                        db.execute(text("""
                            INSERT INTO booking_service (booking_detail_id, service_id, employee_id, quantity, total_price)
                            VALUES (:bdid, :sid, :eid, :qty, :total)
                        """), {
                            'bdid': detail.id,
                            'sid': svc.id,
                            'eid': None,
                            'qty': 1,
                            'total': float(svc.price)
                        })
                        db.commit()

        # Housekeeping task sample
        cleaner = db.query(Employee).filter(Employee.username == 'cleaner').first()
        target_room = db.query(Room).filter(Room.status == 'needs_cleaning').first()
        if target_room and cleaner:
            existing_task = db.query(HousekeepingTask).filter(
                HousekeepingTask.room_id == target_room.id,
                HousekeepingTask.employee_id == cleaner.id,
            ).first()
            if not existing_task:
                task = HousekeepingTask(room_id=target_room.id, employee_id=cleaner.id, status='TODO', notes='Sample seed task')
                db.add(task)
                db.commit()

        print("\nDatabase seeded successfully!")
        print("=" * 40)
        print("Test Accounts (Password for all is 'password123'):")
        print("=" * 40)
        for emp in employees_data:
            print(f"- Role: {emp['role']:<15} | Username: {emp['username']}")
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        db.rollback()
    finally:
        db.close()

def clear_seeded_data(db):
    """Delete seeded data in a safe order to avoid FK constraint errors."""
    print("Clearing seeded data...")
    try:
        # booking_service -> booking_detail -> payment -> booking
        db.execute(text("DELETE FROM booking_service"))
        db.execute(text("DELETE FROM booking_detail"))
        db.execute(text("DELETE FROM payment"))
        db.execute(text("DELETE FROM booking"))

        # housekeeping tasks (may reference room/employee)
        db.execute(text("DELETE FROM housekeeping_task"))

        # rooms, room types, services, employees, guests
        db.execute(text("DELETE FROM room"))
        db.execute(text("DELETE FROM room_type"))
        db.execute(text("DELETE FROM service"))
        db.execute(text("DELETE FROM employee"))
        db.execute(text("DELETE FROM guest"))

        db.commit()
        print("Cleared seeded data.")
    except Exception as e:
        print("Error while clearing seeded data:", e)
        db.rollback()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Seed the database with sample data')
    parser.add_argument('--reset', action='store_true', help='Clear seeded tables before seeding')
    args = parser.parse_args()

    if args.reset:
        db = SessionLocal()
        try:
            clear_seeded_data(db)
        finally:
            db.close()

    seed_database()