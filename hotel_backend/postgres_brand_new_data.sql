-- Brand-new PostgreSQL seed data for the hotel management project.
-- This script truncates existing rows and loads a fresh demo dataset.
-- Run it after the schema has been created in PostgreSQL.

BEGIN;

TRUNCATE TABLE
    booking_service,
    housekeeping_task,
    payment,
    booking_detail,
    booking,
    room,
    service,
    guest,
    employee,
    room_type
RESTART IDENTITY CASCADE;

INSERT INTO room_type (id, name, base_price, max_occupancy) VALUES
    (1, 'Standard', 79.00, 2),
    (2, 'Deluxe', 129.00, 3),
    (3, 'Suite', 219.00, 4),
    (4, 'Family', 179.00, 5);

INSERT INTO employee (id, full_name, position, username, hashed_password, role) VALUES
    (1, 'Ava Chen', 'General Manager', 'admin', '$2b$12$UPfA7JahWlAXKtupryT8geidETKoPTYqtuahcgZdTuCjH5P5OBqDu', 'admin'),
    (2, 'Noah Patel', 'Front Office Manager', 'manager', '$2b$12$UPfA7JahWlAXKtupryT8geidETKoPTYqtuahcgZdTuCjH5P5OBqDu', 'manager'),
    (3, 'Lina Gomez', 'Receptionist', 'receptionist', '$2b$12$UPfA7JahWlAXKtupryT8geidETKoPTYqtuahcgZdTuCjH5P5OBqDu', 'receptionist'),
    (4, 'Marco Silva', 'Housekeeper', 'cleaner', '$2b$12$UPfA7JahWlAXKtupryT8geidETKoPTYqtuahcgZdTuCjH5P5OBqDu', 'housekeeping'),
    (5, 'Sara Ahmed', 'Guest Services', 'waiter', '$2b$12$UPfA7JahWlAXKtupryT8geidETKoPTYqtuahcgZdTuCjH5P5OBqDu', 'waiter');

INSERT INTO guest (id, full_name, email, phone, address) VALUES
    (1, 'John Carter', 'john.carter@example.com', '+1-202-555-0101', '12 Maple Street, New York, NY'),
    (2, 'Maya Singh', 'maya.singh@example.com', '+1-202-555-0102', '88 Lake View Road, Chicago, IL'),
    (3, 'Ethan Brown', 'ethan.brown@example.com', '+1-202-555-0103', '44 Sunset Avenue, Austin, TX'),
    (4, 'Olivia Johnson', 'olivia.johnson@example.com', '+1-202-555-0104', '19 Harbor Drive, Seattle, WA');

INSERT INTO service (id, name, price) VALUES
    (1, 'Breakfast Buffet', 12.00),
    (2, 'Airport Transfer', 35.00),
    (3, 'Spa Massage', 50.00),
    (4, 'Laundry Service', 8.00);

INSERT INTO room (id, room_number, room_type_id, status, floor) VALUES
    (1, '101', 1, 'available', 1),
    (2, '102', 1, 'needs_cleaning', 1),
    (3, '201', 2, 'occupied', 2),
    (4, '301', 3, 'reserved', 3),
    (5, '401', 4, 'available', 4);

INSERT INTO booking (id, guest_id, check_in_date, check_out_date, status, number_of_guests) VALUES
    (1, 1, '2026-06-01', '2026-06-04', 'confirmed', 2),
    (2, 2, '2026-06-10', '2026-06-13', 'checked_in', 3),
    (3, 3, '2026-06-15', '2026-06-17', 'pending', 1);

INSERT INTO booking_detail (id, booking_id, room_id, price_per_night) VALUES
    (1, 1, 1, 79.00),
    (2, 1, 2, 79.00),
    (3, 2, 3, 129.00),
    (4, 3, 4, 219.00);

INSERT INTO payment (id, booking_id, amount, payment_method, payment_date) VALUES
    (1, 1, 158.00, 'credit_card', '2026-05-24 09:15:00'),
    (2, 2, 387.00, 'cash', '2026-05-24 10:05:00');

INSERT INTO booking_service (id, booking_detail_id, service_id, employee_id, quantity, total_price) VALUES
    (1, 1, 1, 5, 2, 24.00),
    (2, 1, 2, 5, 1, 35.00),
    (3, 3, 4, 5, 2, 16.00),
    (4, 4, 3, 4, 1, 50.00);

INSERT INTO housekeeping_task (id, room_id, employee_id, status, notes) VALUES
    (1, 2, 4, 'TODO', 'Deep clean after checkout'),
    (2, 3, 4, 'IN_PROGRESS', 'Refresh minibar and linens'),
    (3, 4, 4, 'DONE', 'Room inspected and ready for guest arrival');

COMMIT;
