# SS2 Final Project Report — Hotel Management System

---

## 2. Project Summary

### What Problem the Project Solves

Small and medium-sized hotels typically rely on spreadsheets or paper records to track room availability, guest information, bookings, and payments. This approach is error-prone, hard to share among staff, and difficult to audit. The **Hotel Management System** replaces that workflow with a web-based platform that lets hotel staff manage every aspect of hotel operations from a single interface — in real time and with data integrity enforced at the database level.

### Target Users

| Role | What they do in the system |
|---|---|
| Admin | Full access: manage rooms, staff, services, view all bookings and payments |
| Receptionist | Create/update guests and bookings, record payments, check room availability |
| Housekeeping | View and update housekeeping task status |

### Main Completed Features

- **Authentication** — JWT-based login/logout; role field embedded in token; protected routes on both backend and frontend.
- **Guest Management** — Full CRUD with email uniqueness validation and paginated search.
- **Room Management** — Room inventory with five status values (`available`, `occupied`, `needs_cleaning`, `maintenance`, `reserved`) and real-time date-range availability checking.
- **Bookings** — Multi-room booking in a single atomic transaction; SQL-level date-conflict detection; booking status lifecycle (`pending → confirmed → checked_in → checked_out / cancelled`).
- **Payments** — Record payments per booking (cash, card, bank transfer, etc.); invoice calculation with room total + service total; balance tracking.
- **Services** — Hotel service catalog with pricing; services can be attached to booking rooms.
- **Employee Management** — Staff CRUD with role-based access control.
- **Housekeeping** — Task assignment to employees with status tracking (`TODO`, `in_progress`, `done`).
- **Dashboard** — Monthly revenue, available room count, total guests, recent booking list, full room-status grid.

### Tech Stack & Architecture (High-Level)

```
Browser (Vanilla JS / HTML5 / CSS3)
        │  Fetch API + JWT ******
        ▼
FastAPI (Python 3.8+)
  ├── Routers  (guests, rooms, bookings, payments, employees,
  │             services, booking_details, housekeeping, auth)
  ├── Services (business logic layer)
  └── SQLAlchemy ORM  ──► PostgreSQL 14+
                              (Alembic migrations)
```

- **Backend:** FastAPI 0.136 + Uvicorn + SQLAlchemy 2.0 + psycopg2-binary + python-jose (JWT) + Passlib (password hashing)
- **Frontend:** Pure HTML5 / CSS3 / ES6 (no framework); Fetch API for all HTTP calls; JWT stored in `localStorage`
- **Database:** PostgreSQL with Alembic for schema migrations and seed scripts for demo data
- **Deployment target:** Render — backend as a Web Service, frontend as a Static Site, database as a Render PostgreSQL instance

### Current Project Status

The core hotel management workflow (guest → room → booking → payment) is fully functional end-to-end. Authentication, role-based access, and all primary CRUD operations are complete. Service assignment to booking rooms is partially implemented (requires a valid `employee_id`). Deployment configuration for Render is in place; the backend runs on Render with PostgreSQL and the frontend is served as a static site.

---

## 3. Progress to Final Outcome

| Phase | Main Tasks | Weekly Progress Status | Final Status | Evidence |
|---|---|---|---|---|
| **Design: ERD, UI, API plan** | Entity-relationship design (Guest, Room, Booking, Payment, Employee, Service, HousekeepingTask), Figma wireframes for all pages, REST API contract per resource | Completed on schedule | ✅ Completed | `models.py` (ERD implemented), Figma files, API documented in `/docs` (FastAPI auto-docs) |
| **Development: Backend** | FastAPI app structure, routers, service layer, SQLAlchemy models, Alembic migrations, seed data, JWT auth, CORS config | In progress (iterative) | ✅ Completed | `hotel_backend/` folder; `routers/`, `services/`, `alembic/` directories; `bulk_seed.py`, `render_migrate.py` |
| **Development: Frontend** | HTML/CSS layout, `api.js` client with field normalisation, `pages.js` per-page rendering, `auth.js` login/logout flow, dashboard stats | In progress (iterative) | ✅ Completed | `frontend booking hotel management/` folder; `api.js`, `pages.js`, `auth.js`, `app.js`, `ui.js` |
| **Development: Integration** | CORS wiring, environment variable handling (`API_BASE_URL`), database URL config for local vs Render, MySQL→PostgreSQL migration utility | In progress | ✅ Completed | `config.js`, `main.py` CORS list, `migrate_mysql_to_postgresql.py`, `render.yaml` |
| **Testing: Bug fixing, user-flow testing** | Manual E2E flows, Python E2E test scripts (`e2e_test.py`, `e2e_more.py`), payment debug script, Playwright/Puppeteer UI tests, API call validation scripts | Planned | ✅ Completed (partial UI automation) | `e2e_test.py`, `e2e_more.py`, `debug_payment.py`, `test_api_calls.py`, `puppeteer_test.js`, `ui_test_playwright.py` |
| **Deployment** | Render backend web service, Render PostgreSQL, Render static site for frontend, environment variable setup, pre-deploy migration command | Planned | ✅ Completed | `render.yaml`, `VERCEL.md`, `README.md` (Render dashboard steps), `render_migrate.py`, `render_start.py` |

---

## 4. What We Learned

### Frontend — Components, State, Routing, Forms, API Calls, UI States

We built the entire frontend with **Vanilla JavaScript** instead of a framework, which forced us to fully understand what frameworks abstract away. We learned how to manage page state manually using a global `App` object and `showPage()` routing function. Forms were handled by reading `FormData` and mapping field names to the API's expected schema. A key insight was implementing a **field normalisation layer** in `api.js`: the backend returns `full_name` but the UI uses `name`, so every guest API call runs through a mapper on both request and response, keeping the UI code clean.

> **Project-specific example:** `api.js` `guests.list()` maps `item.full_name → item.name` and `item.id → item.guest_id` for every item returned, so the UI always works with a consistent shape regardless of what the backend sends.

### Backend — Routes, Controllers, Services, Validation, Error Handling

We learned how FastAPI's dependency injection separates concerns cleanly: routers declare endpoints and HTTP codes, `Depends(get_db)` injects a database session, and all business logic lives in the `services/` layer. Pydantic models enforce input validation automatically — for example the `@field_validator('check_out_date')` on `BookingCreate` raises a clear error if checkout is not after check-in. Error handling uses `HTTPException` with explicit status codes (400, 404, 409, 422).

> **Project-specific example:** `bookings.py` router returns `HTTP 201` on successful creation and `HTTP 400` with a Vietnamese-language detail message when a requested room is unavailable, giving the frontend something meaningful to display.

### Database — Schema, Relationships, Queries, Migrations, Seed Data

We learned how to model a real normalised schema: `Room` references `RoomType`, `BookingDetail` links `Booking` and `Room`, `BookingService` links `BookingDetail`, `Service`, and `Employee`. SQLAlchemy `relationship()` with `back_populates` and `cascade="all, delete-orphan"` keeps referential integrity managed at the ORM level. We used Alembic for schema versioning and wrote a `bulk_seed.py` script to populate a deterministic demo dataset.

> **Project-specific example:** Room availability is checked with a single SQL `NOT EXISTS` subquery in `booking_service.py` that joins `booking_detail` and `booking`, filtering by date overlap and excluding cancelled bookings — far more reliable than doing this in application code.

### Authentication / Authorization

We implemented JWT authentication with `python-jose`. On login, the token payload includes both `sub` (username) and `role`. The `require_role()` helper returns a FastAPI dependency that checks `current_user.role` and raises `HTTP 403 Forbidden` if the caller lacks permission. On the frontend, `api.js` detects `401` responses, clears the stored token, and redirects to the login screen.

> **Project-specific example:** `auth_service.py` `require_role(['admin'])` is injected into employee management endpoints so that only admin users can create or delete staff accounts.

### API Integration and Field Normalisation

The frontend and backend evolved somewhat independently, leading to field name mismatches. We solved this permanently by centralising all HTTP calls in `api.js` with per-resource normalisation functions, so UI components never touch raw backend shapes. This is a pattern used in production API clients (e.g. an "adapter" or "gateway" layer).

### Deployment and Environment Variables

We learned that environment variables must never be hardcoded. `config.py` reads `DATABASE_URL` and `SECRET_KEY` from `.env` locally, and from Render's Environment Variable panel in production. The frontend reads `window.API_BASE_URL` from `config.js`, which Render injects at build time for the static site. We also migrated the database from MySQL to PostgreSQL midway through the project, using a custom migration utility (`migrate_mysql_to_postgresql.py`).

### Git and Teamwork

We used feature branches (`feature/seed-reset`), pull requests for review, and conventional commit messages (`feat:`, `fix:`, `chore:`). We encountered merge conflicts when two team members modified `models.py` simultaneously and learned to resolve them by reading both diffs carefully before choosing which changes to keep.

---

## 5. Technical Challenges and Solutions

### Challenge 1 — Payment Endpoint 500 Error (ENUM column mismatch)

**What happened:** Submitting a payment with `payment_method: "card"` returned HTTP 500 with the database error "Data truncated for column 'payment_method'".

**Why it happened:** The original MySQL schema defined `payment_method` as an `ENUM` with a fixed list of values. When the database was migrated to PostgreSQL, the column was recreated but the allowed values did not include `"card"` — any value outside the original enum caused a truncation error.

**How we solved it:** We changed the column definition in `models.py` to `Column(String(50))` (VARCHAR), which accepts any string value up to 50 characters. The migration was applied with Alembic and the `render_migrate.py` pre-deploy script.

**What changed after the fix:** All payment tests pass with HTTP 201. Payment methods including `"cash"`, `"card"`, and `"bank_transfer"` are all accepted.

**Lesson learned:** ENUMs are rigid and database-specific. Using `VARCHAR` with application-level validation is more portable and flexible.

**Proof:** `debug_payment.py` test script; `models.py` line 60; Known Issues section of `README.md`.

---

### Challenge 2 — CORS Errors Between Frontend and Backend

**What happened:** When opening the frontend in a browser and calling the backend API, all requests failed with `CORS policy: No 'Access-Control-Allow-Origin' header`.

**Why it happened:** Browsers block cross-origin requests by default. The frontend runs on `http://127.0.0.1:5500` and the backend on `http://127.0.0.1:8000` — different ports, so they are different origins. The backend was not returning CORS headers.

**How we solved it:** We added `CORSMiddleware` to `main.py` with an explicit list of allowed origins covering local development ports and the production Render domains. We also added `allow_origin_regex=r"https://.*\.onrender\.com"` so any Render preview URL is automatically allowed.

**What changed after the fix:** API calls from the browser succeed. Adding new Render URLs does not require a code change.

**Lesson learned:** CORS must be configured explicitly on every API server. The regex approach is safer than `allow_origins=["*"]` because it still validates the origin pattern.

**Proof:** `main.py` lines 24–45; `VERCEL.md` deployment notes.

---

### Challenge 3 — MySQL to PostgreSQL Database Migration

**What happened:** The project started development with MySQL. Midway through, the team decided to deploy on Render, which offers managed PostgreSQL but not MySQL. All existing data and the schema had to be moved.

**Why it happened:** The team initially chose MySQL because it was familiar. Render's free-tier managed database offering is PostgreSQL only.

**How we solved it:** We wrote `migrate_mysql_to_postgresql.py`, a utility that reads tables from the MySQL source using SQLAlchemy + pymysql, then inserts them into the PostgreSQL target in foreign-key-safe order, resetting primary-key sequences after the copy. We also generated `postgres_brand_new_data.sql` as a fresh demo dataset for Render deployments.

**What changed after the fix:** The backend runs entirely on PostgreSQL locally and on Render. MySQL is no longer a dependency.

**Lesson learned:** Always choose the deployment target's database engine from the start of the project to avoid migration work. If migration is unavoidable, a script-based approach with sequence resets is safer than a manual dump-and-restore.

**Proof:** `migrate_mysql_to_postgresql.py`, `postgres_brand_new_data.sql`, `render.yaml`, `README.md` "Moving Existing MySQL Data" section.

---

### Challenge 4 — Field Name Inconsistency Between Frontend and Backend

**What happened:** UI components showed blank values or `undefined` in guest and booking tables. The backend returned `full_name` but the frontend expected `name`; the backend returned `booking_id` but the frontend used `id`.

**Why it happened:** The backend followed database column naming conventions (`snake_case` matching model field names) while the UI was designed using more generic names. The two sides evolved independently without an agreed contract.

**How we solved it:** We created a centralised normalisation layer in `api.js`. Every resource (guests, bookings, employees) has a dedicated transform applied to each response object before it reaches the UI. Requests similarly map UI field names back to what the backend expects before sending.

**What changed after the fix:** UI components are decoupled from backend field names. If the backend field name changes, only the normalisation function in `api.js` needs updating — not every component.

**Lesson learned:** Define and document a shared API contract early. Until that contract is stable, use an adapter layer to isolate both sides from each other's naming decisions.

**Proof:** `api.js` `guests.list()`, `guests.get()`, `guests.create()`, and `employees.normalize()`.

---

## 6. Planned Work vs Final Result

| Item | Original Plan | Final Result | Reason if Incomplete |
|---|---|---|---|
| Guest CRUD | Required | ✅ Completed | — |
| Room CRUD + availability check | Required | ✅ Completed | — |
| Booking creation (multi-room) | Required | ✅ Completed | — |
| Booking status management | Required | ✅ Completed | — |
| Payment recording + invoice | Required | ✅ Completed | — |
| Employee management | Required | ✅ Completed | — |
| JWT Login / Logout | Required | ✅ Completed | — |
| Role-based access control | Required | ✅ Completed | — |
| Hotel service catalog | Required | ✅ Completed | — |
| Service assignment to booking rooms | Required | ⚠️ Partial | Requires a valid `employee_id`; the UI does not yet expose a staff selector on the service form, so this step must be done via the API directly |
| Housekeeping task management | Planned | ✅ Completed | — |
| Dashboard (stats + room grid) | Planned | ✅ Completed | — |
| Admin-only employee controls | Planned | ✅ Completed | — |
| Database migration (MySQL → PostgreSQL) | Not originally planned | ✅ Completed | Required for Render deployment |
| Render deployment (backend + DB) | Planned | ✅ Completed | — |
| Render deployment (frontend static site) | Planned | ✅ Completed | — |
| Automated E2E test suite | Planned | ⚠️ Partial | Python E2E scripts cover the main booking flow; Playwright/Puppeteer UI automation scripts exist but require a running browser environment and were not integrated into CI |
| CI/CD pipeline | Not in original scope | ⚠️ Not completed | Would require GitHub Actions configuration; not prioritised given deployment time constraints |
| API rate limiting | Not in original scope | ❌ Not completed | Noted as a future improvement; not blocking for the current use case |
