from sqlalchemy import text, inspect
from db import SessionLocal, engine, Base
from models import Employee, RoomType, Room, Guest
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
        SET floor = CAST(SUBSTRING(room_number, 1, 1) AS UNSIGNED)
        WHERE floor IS NULL
          AND room_number REGEXP '^[0-9]'
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
            if not existing:
                emp = Employee(
                    username=emp_data["username"],
                    hashed_password=get_password_hash(emp_data["password"]),
                    full_name=emp_data["full_name"],
                    position=emp_data["position"],
                    role=emp_data["role"]
                )
                db.add(emp)
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

if __name__ == "__main__":
    seed_database()