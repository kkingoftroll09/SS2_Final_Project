# SS2 Final Project - Hotel Management System

## Project name
SS2 Final Project - Hotel Management System

## Short description
A full-stack hotel management system for managing guests, rooms, bookings, payments, employees, and hotel services.

## Member list
- Dao Quoc Yen – 2301040205 – Backend/ Database
- Nguyen Thai Tuan – 2301040192 – Frontend
- Nguyen Hoai Nam – 2301040130 – Tester/ Deploy

## Tech stack
- Backend: FastAPI, SQLAlchemy, Uvicorn, Alembic
- Frontend: HTML, CSS, JavaScript (vanilla)
- Database: PostgreSQL
- Utilities: Python scripts for migration/seed and end-to-end checks

## Main features
- Authentication with role-based access
- Guest management (CRUD)
- Room management and availability checks
- Booking management with status updates
- Payment management and invoice tracking
- Employee management
- Hotel service management

## Overall project structure
```text
SS2_Final_Project/
├── hotel_backend/                      # FastAPI backend + DB logic
│   ├── routers/                        # API routes
│   ├── services/                       # Business logic
│   ├── alembic/                        # Database migrations
│   ├── main.py                         # Backend entry
│   ├── render_migrate.py               # Migration helper
│   └── seed_data.py                    # Demo seed data
├── frontend booking hotel management/  # Frontend source
│   ├── index.html
│   ├── app.js
│   ├── api.js
│   ├── auth.js
│   ├── pages.js
│   └── style.css
├── e2e_test.py
├── e2e_more.py
└── README.md
```

## Installation steps and required tools
Required tools:
- Git
- Python 3.10+
- pip
- PostgreSQL 14+

Steps:
1. Clone repository.
2. Create and activate Python virtual environment.
3. Install backend dependencies:
   ```bash
   cd hotel_backend
   pip install -r requirements.txt
   cd ..
   ```

## Environment variable setup using `.env.example`
1. Copy `.env.example` to `.env` in the project root.
2. Update values for your local PostgreSQL database.

Example:
```bash
cp .env.example .env
```

## How to run frontend
From project root:
```bash
cd "frontend booking hotel management"
python -m http.server 5500
```
Open: `http://127.0.0.1:5500`

## How to run backend
From project root:
```bash
python -m uvicorn hotel_backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API docs: `http://127.0.0.1:8000/docs`

## How to set up or migrate/seed the database
Run migration helper:
```bash
python hotel_backend/render_migrate.py
```

Seed demo data:
```bash
python hotel_backend/seed_data.py
```

## How to run the full system from a clean machine
1. Install required tools (Git, Python, pip, PostgreSQL).
2. Clone repo.
3. Create PostgreSQL database.
4. Copy `.env.example` to `.env` and fill DB/secret values.
5. Install backend dependencies (`pip install -r hotel_backend/requirements.txt`).
6. Run migrations (`python hotel_backend/render_migrate.py`).
7. Seed data (`python hotel_backend/seed_data.py`).
8. Start backend (`python -m uvicorn hotel_backend.main:app --host 127.0.0.1 --port 8000 --reload`).
9. Start frontend (`cd "frontend booking hotel management" && python -m http.server 5500`).
10. Open `http://127.0.0.1:5500`.

## Demo account, if login is required
After seeding data:
- Username: `admin`
- Password: `password123`

## Known issues
- Payment/service flows may require valid related records (for example booking and employee) to avoid request errors.
- Integration tests (for example `python e2e_test.py`) require backend running at `http://127.0.0.1:8000`.
