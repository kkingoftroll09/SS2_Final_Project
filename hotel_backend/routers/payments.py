from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
import services.payment_service as payment_service

router = APIRouter()

class PaymentCreate(BaseModel):
    amount: float
    payment_method: str = "cash"


class PaymentUpdate(BaseModel):
    amount: float
    payment_method: str = "cash"


@router.get("/payments")
async def list_payments(db: Session = Depends(get_db)):
    return payment_service.list_payments(db)


@router.get("/payments/{payment_id}")
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = payment_service.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(404, "Payment not found")
    return payment


@router.put("/payments/{payment_id}")
async def update_payment(payment_id: int, payment: PaymentUpdate, db: Session = Depends(get_db)):
    updated = payment_service.update_payment(db, payment_id, payment.amount, payment.payment_method)
    if not updated:
        raise HTTPException(404, "Payment not found")
    return updated

@router.post("/bookings/{booking_id}/payments")
async def add_payment(booking_id: int, payment: PaymentCreate, db: Session = Depends(get_db)):
    payment_id = payment_service.add_payment(db, booking_id, payment.amount, payment.payment_method)
    if not payment_id:
        raise HTTPException(400, "Cannot add payment")
    return {"payment_id": payment_id, **payment.model_dump()}

@router.get("/bookings/{booking_id}/payments")
async def get_payments(booking_id: int, db: Session = Depends(get_db)):
    return payment_service.get_payments_for_booking(db, booking_id)

@router.get("/bookings/{booking_id}/invoice")
async def get_invoice(booking_id: int, db: Session = Depends(get_db)):
    invoice = payment_service.get_invoice(db, booking_id)
    if not invoice:
        raise HTTPException(404, "Booking not found")
    return invoice