import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Load hotel_backend .env
import sys
sys.path.insert(0, 'hotel_backend')
load_dotenv('hotel_backend/.env')

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME = os.getenv('DB_NAME', 'hotel_management')

conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = conn.cursor()

try:
    cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='booking' AND COLUMN_NAME='number_of_guests'", (DB_NAME,))
    exists = cursor.fetchone()[0]
    if not exists:
        cursor.execute('ALTER TABLE booking ADD COLUMN number_of_guests INT NULL DEFAULT 1')
        conn.commit()
        print('✓ number_of_guests column added to booking')
    else:
        print('number_of_guests column already exists')
except Exception as e:
    print('Error:', e)
    conn.rollback()
finally:
    cursor.close()
    conn.close()
