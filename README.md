# Hotel Management System

A full-stack hotel management application with guest booking, room management, payments, and employee administration. Built with FastAPI (backend) and vanilla JavaScript (frontend).

## 🏗️ Project Structure

```
SS2_Project_New/
├── hotel_backend/              # FastAPI backend
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Database configuration
│   ├── db.py                  # SQLAlchemy setup
│   ├── models.py              # Database models (Guest, Room, Booking, Payment, etc.)
│   ├── requirements.txt        # Python dependencies
│   ├── routers/               # API endpoints
│   │   ├── guests.py          # Guest CRUD endpoints
│   │   ├── rooms.py           # Room management (availability checking)
│   │   ├── bookings.py        # Booking creation and management
│   │   ├── payments.py        # Payment recording
│   │   ├── employees.py       # Staff management
│   │   ├── hotel_services.py  # Service catalog
│   │   ├── booking_details.py # Add services to bookings
│   │   ├── housekeeping.py    # Housekeeping tasks
│   │   └── auth.py            # Authentication endpoints
│   ├── services/              # Business logic layer
│   │   ├── guest_service.py
│   │   ├── room_service.py
│   │   ├── booking_service.py
│   │   ├── payment_service.py
│   │   └── ... (other services)
│   └── alembic/               # Database migrations
├── frontend booking hotel management/  # Vanilla JS frontend
│   ├── index.html             # Main HTML page
│   ├── style.css              # Styling
│   ├── api.js                 # API client with field normalization
│   ├── ui.js                  # UI component handling
│   ├── pages.js               # Page implementations
│   ├── app.js                 # Frontend app entry point
│   └── auth.js                # Authentication logic
├── debug_payment.py           # Payment testing script
├── e2e_test.py               # Basic end-to-end test
├── e2e_more.py               # Extended E2E scenarios
└── fix_db_schema.py          # Database schema migration utility
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 5.7+ (running on localhost:3306)
- Node.js (optional, for serving frontend)

### 1. Setup Backend

```bash
cd hotel_backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Database

Create MySQL database:
```sql
CREATE DATABASE hotel_management;
```

Update `config.py`:
```python
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "hotel_management"
```

### 3. Run Migrations

```bash
cd alembic
alembic upgrade head
cd ..
```

### 4. Start Backend (Port 8000)

```bash
# Windows (PowerShell helper)
./start_backend.ps1

# Or directly (from project root):
python -m uvicorn hotel_backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Start Frontend (Port 5500)

```bash
./start_frontend.ps1

# Or directly:
cd "frontend booking hotel management"
python -m http.server 5500
```

### Quick Helpers

- `start_backend.ps1`: PowerShell helper to start the backend with the correct path.
- `start_frontend.ps1`: PowerShell helper to serve the frontend on port 5500.

Open browser: `http://127.0.0.1:5500`

## Deploying on Render

Use two services so the backend and frontend stay separate:

### Backend Web Service

- Root directory: `hotel_backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add environment variables for your database: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- Use an external MySQL host. Render does not provide a managed MySQL database.

If Render says it cannot find `requirements.txt`, the service is almost always pointed at the repo root instead of `hotel_backend`. Fix it by setting the service Root Directory to `hotel_backend` and keeping the build command relative to that folder.

### Frontend Static Site

- Root directory: `frontend booking hotel management`
- Build command: `echo "No build step"`
- Publish directory: `.`
- Set `window.API_BASE_URL` in the frontend to your Render backend URL before deploying the static site

### Render Dashboard Steps (exact)

1. Sign in to Render and go to the Dashboard.

2. Create the Backend service:
	- Click "New" → "Web Service".
	- Connect your GitHub repo (`kkingoftroll09/SS2_Final_Project`) and select branch `main`.
	- Root Directory: `hotel_backend`
	- Environment: `Python 3`
	- Build Command: `pip install -r requirements.txt`
	- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
	- Advanced: set `Health check path` to `/` or `/docs`.
	- Click "Create Web Service".

3. Set Backend environment variables (Service → Environment → Environment Variables):
	- `DB_HOST` (secret) — your MySQL host
	- `DB_PORT` = `3306` (or your DB port)
	- `DB_USER` (secret)
	- `DB_PASSWORD` (secret)
	- `DB_NAME` = `hotel_management`
	- `SECRET_KEY` (secret)

4. Add a deploy hook to run migrations automatically (optional):
	- In the backend service settings, under "Advanced" → "Pre-deploy commands", add:
	  ```
	  alembic upgrade head
	  ```
	- Alternatively, keep migrations manual and run `alembic upgrade head` from the Render shell after the service is running.

5. Create the Frontend static site:
	- Click "New" → "Static Site".
	- Connect the same GitHub repo and branch `main`.
	- Root Directory: `frontend booking hotel management`
	- Build Command: `echo "No build step"`
	- Publish Directory: `.`
	- Optionally set an Environment Variable `API_BASE_URL` to your backend URL; otherwise edit `frontend booking hotel management/config.js` before deploying.
	- Click "Create Static Site".

6. After the backend deploys, copy the backend service URL (e.g. `https://<your-backend>.onrender.com`) and update the frontend `API_BASE_URL` (either via the static site's env vars or by editing `config.js` and redeploying the static site).

7. Verify:
	- Open the frontend static site URL and confirm the UI loads and API calls succeed.
	- Check backend logs on Render for any migration or DB connection errors.


### What to commit to GitHub

- Commit the source folders, migrations, README, and helper scripts.
- Do not commit virtual environments, cache folders, `node_modules`, secrets, or the accidental root `requirements.txt` created by `pip freeze`.

## 📋 Core Features

### Guest Management
- **Create/Read/Update/Delete** guests
- Email uniqueness validation
- Fields: full_name, email, phone, address

### Room Management
- Room inventory with status tracking
- Real-time availability checking by date range
- Room types: Standard, Deluxe, Suite, Family
- Status: available, occupied, needs_cleaning, maintenance, reserved

### Bookings
- Multi-room bookings in single transaction
- Automatic room availability validation
- Date conflict detection via SQL query
- Status: pending, confirmed, checked_in, checked_out, cancelled

### Payments
- Record payments by method (cash, card, bank transfer, etc.)
- Invoice calculation with room + service totals
- Payment tracking per booking
- Balance calculation

### Employees
- Staff management with roles (admin, receptionist, housekeeping, etc.)
- Username/password authentication
- Role-based access control

### Services
- Hotel service catalog (room service, spa, laundry, etc.)
- Pricing per service
- Attach services to specific rooms in a booking

## 🔌 API Endpoints

### Authentication
```
POST /api/auth/login                 Login (returns JWT token)
POST /api/auth/logout                Logout
```

### Guests
```
GET    /api/guests                   List all guests (paginated)
GET    /api/guests/{guest_id}        Get guest details
POST   /api/guests                   Create guest
PUT    /api/guests/{guest_id}        Update guest
DELETE /api/guests/{guest_id}        Delete guest
```

### Rooms
```
GET    /rooms                        List rooms (optional: ?check_in_date=YYYY-MM-DD&check_out_date=YYYY-MM-DD)
GET    /rooms/{room_id}              Get room details
POST   /rooms                        Create room
PUT    /rooms/{room_id}              Update room
DELETE /rooms/{room_id}              Delete room
```

### Bookings
```
GET    /api/bookings                 List all bookings
GET    /api/bookings/{booking_id}    Get booking details
POST   /api/bookings                 Create booking (with room_ids array)
PUT    /api/bookings/{booking_id}    Update booking
DELETE /api/bookings/{booking_id}    Delete booking
PUT    /api/bookings/{booking_id}/status  Update booking status
GET    /bookings/{booking_id}/invoice     Get invoice (room_total, service_total, paid, balance)
```

### Payments
```
GET    /payments                     List all payments
GET    /payments/{payment_id}        Get payment
POST   /payments                     Create payment
POST   /bookings/{booking_id}/payments    Add payment to booking
GET    /bookings/{booking_id}/payments    List booking payments
```

### Services
```
GET    /services                     List services
POST   /services                     Create service
POST   /booking-details/{id}/services  Add service to booking room
```

## 🔐 Authentication

The app uses JWT tokens with OAuth2 PasswordBearer:

1. Login: `POST /api/auth/login` with username/password (form-encoded)
2. Receive JWT token
3. Include token in Authorization header: `Authorization: Bearer <token>`
4. Token expires after 24 hours

## 🧪 Testing

### Run Basic E2E Test
```bash
python e2e_test.py
```

### Run Extended Scenarios
```bash
python e2e_more.py
```

This runs 3 comprehensive scenarios:
1. **Full-pay invoice**: Create guest → booking → payment (full amount)
2. **Add service**: Create booking → add service → verify invoice updated
3. **Cancel booking**: Create booking → cancel → verify room becomes available

### Test Payment Endpoint Directly
```bash
python debug_payment.py
```

## 🐛 Known Issues & Fixes

### Payment 500 Error (FIXED ✓)
- **Issue**: Payment endpoint returned 500 with "Data truncated for column 'payment_method'"
- **Cause**: Database column was ENUM with limited values
- **Fix Applied**: Modified `payment_method` to VARCHAR(100) via `fix_db_schema.py`
- **Status**: All payment tests now pass (201 response, 'card' method accepted)

### Service Assignment (PARTIAL)
- Services can be created and listed
- Adding services to booking rooms requires both service_id and employee_id
- May need staff assignment before services can be fully added

## 🔧 Database Schema

Key tables:
- **Guest**: id, full_name, email, phone, address
- **Room**: id, room_number, room_type, status, price_per_night
- **Booking**: id, guest_id, check_in_date, check_out_date, status
- **BookingDetail**: id, booking_id, room_id, price
- **Payment**: id, booking_id, amount, payment_method, payment_date
- **HotelService**: id, service_name, service_price, description
- **Employee**: id, username, hashed_password, role, email

## 📝 Frontend Pages

- **Dashboard**: Stats overview (bookings by month, available rooms, revenue)
- **Guests**: CRUD operations for guest records
- **Rooms**: View and manage room inventory
- **Bookings**: Create multi-room bookings, manage status
- **Payments**: Record and track payments per booking
- **Employees**: Manage staff (admin only)
- **Services**: View and create hotel services

## 🌐 API Response Normalization

The frontend `api.js` normalizes field names for consistency:
- Backend `full_name` ↔ Frontend `name`
- Backend `guest_id` ↔ Frontend `id` (in guest context)
- Backend `booking_id` ↔ Frontend `id` (in booking context)
- Automatic conversion on request/response

## 📊 Tech Stack

**Backend:**
- FastAPI 0.136.1
- Uvicorn 0.47.0
- SQLAlchemy 2.0.49
- PyMySQL 1.1.3
- Alembic (migrations)
- Passlib (password hashing)
- python-jose (JWT)

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript (ES6+)
- Fetch API

**Database:**
- MySQL 5.7+

## 🚢 Deployment Notes

- Backend requires `.env` or environment variables for database credentials
- CORS is enabled for frontend origins
- JWT tokens should be stored in browser localStorage
- Database backups recommended before production use
- API rate limiting not currently implemented

## 📞 Support

For issues or questions:
1. Check test outputs (`e2e_test.py`, `e2e_more.py`)
2. Review database logs in MySQL
3. Check uvicorn terminal for backend errors
4. Browser console for frontend errors
