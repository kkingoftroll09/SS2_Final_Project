from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routers import (
    room_types,
    rooms,
    guests,
    bookings,
    hotel_services,
    booking_details,
    payments,
    employees,
    auth,
    housekeeping
)

app = FastAPI(
    title="Hotel Management API",
    description="Hệ thống quản lý khách sạn - Quản lý phòng, khách hàng, đặt phòng, dịch vụ và thanh toán",
    version="1.0.0"
)

allowed_origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://ss2-final-project.onrender.com",
]

extra_origins = os.getenv("FRONTEND_CORS_ORIGINS", "")
if extra_origins:
    allowed_origins.extend(
        origin.strip() for origin in extra_origins.split(",") if origin.strip()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(room_types.router,      tags=["Phòng - Room Types"])
app.include_router(rooms.router,           tags=["Phòng - Rooms"])
app.include_router(guests.router,          tags=["Khách hàng - Guests"])
app.include_router(bookings.router,        tags=["Đặt phòng - Bookings"])
app.include_router(hotel_services.router,        tags=["Dịch vụ - Services"])
app.include_router(booking_details.router, tags=["Dịch vụ theo phòng"])
app.include_router(payments.router,        tags=["Thanh toán - Payments"])
app.include_router(employees.router,       tags=["Nhân viên - Employees"])
app.include_router(auth.router,            tags=["Xác thực - Auth"])
app.include_router(housekeeping.router,    tags=["Buồng phòng - Housekeeping"])

@app.get("/", tags=["Default"])
async def root():
    return {
        "message": "Hotel Management API is running successfully! 🏨",
        "docs": "/docs"
    }


@app.head("/")
async def root_head():
    return {}


@app.get("/health", tags=["Default"])
async def health_check():
    return {"status": "ok"}