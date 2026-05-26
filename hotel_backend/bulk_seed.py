from datetime import date, timedelta
from db import SessionLocal
from models import Guest, Booking, BookingDetail, Payment, Room, RoomType


def ensure_guest(db, full_name, email, phone, address):
    g = db.query(Guest).filter(Guest.email == email).first()
    if g:
        return g
    g = Guest(full_name=full_name, email=email, phone=phone, address=address)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def create_booking_if_missing(db, guest_id, room_id, check_in, check_out, guests=2):
    exists = db.query(Booking).filter(
        Booking.guest_id == guest_id,
        Booking.check_in_date == check_in,
        Booking.check_out_date == check_out,
    ).first()
    if exists:
        return exists

    booking = Booking(guest_id=guest_id, check_in_date=check_in, check_out_date=check_out, status='pending', number_of_guests=guests)
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # price
    room = db.query(Room).filter(Room.id == room_id).first()
    price = 75.0
    if room and getattr(room, 'room_type', None) and getattr(room.room_type, 'base_price', None) is not None:
        price = float(room.room_type.base_price)

    detail = BookingDetail(booking_id=booking.id, room_id=room_id, price_per_night=price)
    db.add(detail)
    db.commit()
    db.refresh(detail)

    nights = (check_out - check_in).days
    total = price * nights
    payment = Payment(booking_id=booking.id, amount=round(total,2), payment_method='card')
    db.add(payment)
    db.commit()

    return booking


def run_bulk_seed():
    db = SessionLocal()
    try:
        print('Starting bulk seeding...')
        base_in = date.today() + timedelta(days=30)
        base_out = base_in + timedelta(days=2)

        guests = [
            ('Alice Example', 'alice@example.com', '+1 555 2001', '10 Seed Ln'),
            ('Bob Sample', 'bob@example.com', '+1 555 2002', '11 Seed Ln'),
            ('Carol Demo', 'carol@example.com', '+1 555 2003', '12 Seed Ln'),
            ('Dan Mock', 'dan@example.com', '+1 555 2004', '13 Seed Ln'),
            ('Eve Test', 'eve@example.com', '+1 555 2005', '14 Seed Ln'),
        ]

        created = []
        rooms = db.query(Room).all()
        room_cycle = [r.id for r in rooms] or []

        for i, g in enumerate(guests):
            guest = ensure_guest(db, g[0], g[1], g[2], g[3])
            if not room_cycle:
                print('No rooms available in DB; skipping booking creation')
                continue
            room_id = room_cycle[i % len(room_cycle)]
            check_in = base_in + timedelta(days=i)
            check_out = base_out + timedelta(days=i)
            booking = create_booking_if_missing(db, guest.id, room_id, check_in, check_out)
            created.append((guest.email, booking.id))

        print('Bulk seed finished. Created entries:')
        for c in created:
            print('-', c)

    finally:
        db.close()


if __name__ == '__main__':
    run_bulk_seed()
