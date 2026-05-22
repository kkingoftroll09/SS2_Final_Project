from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, TIMESTAMP, text
from sqlalchemy.orm import relationship
from db import Base

class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    position = Column(String(100))
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(20), default='receptionist')

class RoomType(Base):
    __tablename__ = "room_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    max_occupancy = Column(Integer, nullable=True)

class Room(Base):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), nullable=False, unique=True)
    room_type_id = Column(Integer, ForeignKey("room_type.id"))
    status = Column(String(20), default="available")
    floor = Column(Integer, nullable=True)
    
    room_type = relationship("RoomType")

class Booking(Base):
    __tablename__ = "booking"
    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, ForeignKey("guest.id"), index=True)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    status = Column(String(50), default="pending")
    number_of_guests = Column(Integer, nullable=True, default=1)
    
    details = relationship("BookingDetail", back_populates="booking", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")
    guest = relationship("Guest")

class BookingDetail(Base):
    __tablename__ = "booking_detail"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("booking.id"))
    room_id = Column(Integer, ForeignKey("room.id"))
    price_per_night = Column(Numeric(10, 2), nullable=False)
    
    booking = relationship("Booking", back_populates="details")
    room = relationship("Room")

class Payment(Base):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("booking.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50))
    payment_date = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    
    booking = relationship("Booking", back_populates="payments")

class BookingService(Base):
    __tablename__ = "booking_service"
    id = Column(Integer, primary_key=True, index=True)
    booking_detail_id = Column(Integer, ForeignKey("booking_detail.id"))
    service_id = Column(Integer, ForeignKey("service.id"))
    employee_id = Column(Integer, ForeignKey("employee.id"))
    quantity = Column(Integer, default=1)
    total_price = Column(Numeric(10, 2), nullable=False)

class Service(Base):
    __tablename__ = "service"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class Guest(Base):
    __tablename__ = "guest"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    address = Column(Text)

class HousekeepingTask(Base):
    __tablename__ = "housekeeping_task"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("room.id"))
    employee_id = Column(Integer, ForeignKey("employee.id"))
    status = Column(String(20), default="TODO")
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    room = relationship("Room")
    employee = relationship("Employee")
