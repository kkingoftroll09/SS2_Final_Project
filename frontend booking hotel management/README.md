# Aurum Hotel — Management Suite

Full-stack hotel management frontend (HTML/CSS/JS) connected to a FastAPI backend.

---

## Project Structure

```
hotel-frontend/
├── index.html          ← Main entry point (app shell + auth)
├── css/
│   └── style.css       ← All styles (dark theme, components)
├── js/
│   ├── api.js          ← FastAPI client (all endpoints)
│   ├── ui.js           ← Toast, Modal, Confirm, Validation
│   ├── auth.js         ← Login & Register pages
│   ├── pages.js        ← All CRUD pages (Guests, Rooms, Bookings…)
│   └── app.js          ← App shell, routing, session
└── backend/
    ├── main.py         ← FastAPI app (starter with in-memory DB)
    └── requirements.txt
```

---

## Frontend Setup

Open `index.html` directly in a browser — **no build step needed**.

To configure the backend URL (default: `http://localhost:8000`), add before the scripts:
```html
<script>window.API_BASE_URL = 'http://your-server:8000';</script>
```

The repo also includes `config.js`, which sets the local default to `http://127.0.0.1:8000`. Update that single file when you deploy to Render.

---

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Features

| Module | List | Search | Create | Edit | Delete |
|--------|------|--------|--------|------|--------|
| Guests | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rooms | ✓ | ✓ | ✓ | ✓ | ✓ |
| Bookings | ✓ | ✓ | ✓ | ✓ | ✓ |
| Services | ✓ | ✓ | ✓ | ✓ | ✓ |
| Employees | ✓ | ✓ | ✓ | ✓ | ✓ |
| Payments | ✓ | ✓ | ✓ | ✓ | — |
| Dashboard | ✓ | — | — | — | — |

### Frontend Validation
- Required fields, email format, phone format
- Positive/non-negative numbers
- Check-out must be after check-in
- Real-time live validation on blur + input
- Form-level error summary from API responses

### Auth
- JWT-based (Bearer token stored in `localStorage`)
- Login / Register with full validation
- Session persistence across page refresh
- Auto-redirect to login on 401

---

## Connecting to a Real Database

The `backend/main.py` uses in-memory dicts for simplicity. To connect to PostgreSQL:

1. Install: `pip install sqlalchemy psycopg2-binary alembic`
2. Replace `fake_users`, `guests_db`, etc. with SQLAlchemy models
3. Replace the `make_crud` factory calls with proper router files

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login (returns JWT) |
| GET | `/auth/me` | Current user info |
| GET/POST | `/guests` | List / create guests |
| GET/PUT/DELETE | `/guests/{id}` | Get / update / delete |
| GET/POST | `/rooms` | List / create rooms |
| GET/POST | `/bookings` | List / create bookings |
| GET/POST | `/services` | List / create services |
| GET/POST | `/employees` | List / create employees |
| GET/POST | `/payments` | List / create payments |
| GET | `/dashboard/stats` | Dashboard summary |
