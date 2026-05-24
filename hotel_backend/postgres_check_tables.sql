-- PostgreSQL inspection script for the hotel project database.
-- It lists the project tables, row counts, and a small sample of rows.
-- Run this against your PostgreSQL database after migration.

SELECT 'employee' AS table_name, COUNT(*) AS row_count FROM employee
UNION ALL SELECT 'room_type', COUNT(*) FROM room_type
UNION ALL SELECT 'room', COUNT(*) FROM room
UNION ALL SELECT 'guest', COUNT(*) FROM guest
UNION ALL SELECT 'booking', COUNT(*) FROM booking
UNION ALL SELECT 'booking_detail', COUNT(*) FROM booking_detail
UNION ALL SELECT 'payment', COUNT(*) FROM payment
UNION ALL SELECT 'service', COUNT(*) FROM service
UNION ALL SELECT 'booking_service', COUNT(*) FROM booking_service
UNION ALL SELECT 'housekeeping_task', COUNT(*) FROM housekeeping_task
ORDER BY table_name;

-- Sample rows for each project table
SELECT 'employee' AS table_name, * FROM employee ORDER BY id LIMIT 5;
SELECT 'room_type' AS table_name, * FROM room_type ORDER BY id LIMIT 5;
SELECT 'room' AS table_name, * FROM room ORDER BY id LIMIT 5;
SELECT 'guest' AS table_name, * FROM guest ORDER BY id LIMIT 5;
SELECT 'booking' AS table_name, * FROM booking ORDER BY id LIMIT 5;
SELECT 'booking_detail' AS table_name, * FROM booking_detail ORDER BY id LIMIT 5;
SELECT 'payment' AS table_name, * FROM payment ORDER BY id LIMIT 5;
SELECT 'service' AS table_name, * FROM service ORDER BY id LIMIT 5;
SELECT 'booking_service' AS table_name, * FROM booking_service ORDER BY id LIMIT 5;
SELECT 'housekeeping_task' AS table_name, * FROM housekeeping_task ORDER BY id LIMIT 5;
