Vercel deployment notes (frontend)

- Project root for Vercel: set to the repository root, but override the Project Root to `frontend booking hotel management` (this repo uses a space).
- Framework Preset: "Other" / Static Site
- Build Command: leave empty or use `echo "No build step"`
- Output Directory: `.`

Environment variables to set in Vercel (Project Settings → Environment Variables):

- `API_BASE_URL` : URL of your backend (e.g. `https://your-backend.example.com`). The frontend uses this to talk to the FastAPI API.

Notes / recommendations:

- The frontend is plain static files (HTML/JS/CSS). Vercel will serve them as-is.
- The backend (`hotel_backend`) is FastAPI and requires a Postgres DB — keep it on Render/Railway/Heroku or another provider and point `API_BASE_URL` to it.
- Ensure your backend's `FRONTEND_CORS_ORIGINS` environment variable includes the Vercel domain (e.g. `https://<your-project>.vercel.app`) so the frontend can call the API.
- Consider renaming the frontend folder to remove spaces (e.g. `frontend-booking-hotel-management`) to simplify config and avoid issues with some tooling. If you rename, update `vercel.json` accordingly.

Quick Vercel import steps:

1. In Vercel, click "New Project" → Import Git Repository (connect GitHub if needed).
2. Under "Root Directory" enter: `frontend booking hotel management` (or the renamed folder).
3. Set Framework Preset → Other, leave Build Command empty, set Output Directory to `.`.
4. Add the `API_BASE_URL` env var and deploy.
