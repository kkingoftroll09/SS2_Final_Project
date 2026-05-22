import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Get DB config from hotel_backend/.env
import sys
sys.path.insert(0, 'hotel_backend')
load_dotenv('hotel_backend/.env')

db_host = os.getenv('DB_HOST', '127.0.0.1')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'root')
db_name = os.getenv('DB_NAME', 'hotel_management')

conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
cursor = conn.cursor()

# Modify the payment_method column to VARCHAR(100)
try:
    cursor.execute('ALTER TABLE payment MODIFY COLUMN payment_method VARCHAR(100) NULL')
    conn.commit()
    print('✓ payment_method column modified to VARCHAR(100)')
except Exception as e:
    print('Error:', e)
    conn.rollback()
finally:
    cursor.close()
    conn.close()
