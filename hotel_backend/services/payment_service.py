from sqlalchemy.orm import Session
from sqlalchemy import text
from models import Payment


def _payment_to_dict(payment: Payment):
    return {
        "payment_id": payment.id,
        "id": payment.id,
        "booking_id": payment.booking_id,
        "amount": float(payment.amount),
        "payment_method": payment.payment_method,
        "payment_date": payment.payment_date,
        "transaction_id": None,
        "status": "completed",
    }

def add_payment(db: Session, booking_id: int, amount: float, payment_method: str):
    payment = Payment(booking_id=booking_id, amount=amount, payment_method=payment_method)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment.id


def get_payment(db: Session, payment_id: int):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    return _payment_to_dict(payment) if payment else None


def list_payments(db: Session):
    payments = db.query(Payment).order_by(Payment.payment_date.desc()).all()
    return [_payment_to_dict(p) for p in payments]


def update_payment(db: Session, payment_id: int, amount: float, payment_method: str):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return None
    payment.amount = amount
    payment.payment_method = payment_method
    db.commit()
    db.refresh(payment)
    return _payment_to_dict(payment)

def get_payments_for_booking(db: Session, booking_id: int):
    payments = db.query(Payment).filter(Payment.booking_id == booking_id).order_by(Payment.payment_date.desc()).all()
    return [_payment_to_dict(p) for p in payments]

def get_invoice(db: Session, booking_id: int):
    booking = db.execute(text("SELECT status FROM booking WHERE id = :id"), {"id": booking_id}).fetchone()
    if not booking:
        return None

    room_total = db.execute(text("""
        SELECT SUM(price_per_night * DATEDIFF(b.check_out_date, b.check_in_date)) as room_total
        FROM booking_detail bd
        JOIN booking b ON bd.booking_id = b.id
        WHERE bd.booking_id = :id
    """), {"id": booking_id}).scalar() or 0

    service_total = db.execute(text("""
        SELECT SUM(total_price) as service_total
        FROM booking_service bs
        JOIN booking_detail bd ON bs.booking_detail_id = bd.id
        WHERE bd.booking_id = :id
    """), {"id": booking_id}).scalar() or 0

    paid = db.execute(text("""
        SELECT SUM(amount) as paid FROM payment WHERE booking_id = :id
    """), {"id": booking_id}).scalar() or 0

    grand_total = float(room_total) + float(service_total)
    balance = grand_total - float(paid)

    return {
        "booking_id": booking_id,
        "room_total": round(float(room_total), 2),
        "service_total": round(float(service_total), 2),
        "grand_total": round(grand_total, 2),
        "paid": round(float(paid), 2),
        "balance": round(balance, 2),
        "status": booking.status
    }