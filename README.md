# Job-Board
Job Board is a platform where employers can post job listings, and candidates can apply for those positions.

## Environment Variables Setup

### Required Environment Variables

Create a `.env` file in the `backend/` directory or set these environment variables:

#### Database Configuration
```bash
# For SQLite (development)
export DATABASE_URL="sqlite:///app.db"

# For PostgreSQL (production/docker)
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
```

#### Flask Configuration
```bash
export FLASK_APP="app.wsgi:app"  # or "run:app" if using run.py
export FLASK_ENV="development"
```

#### Security Keys
```bash
export SECRET_KEY="your-secret-key-here"
export JWT_SECRET_KEY="your-jwt-secret-key-here"
```

#### JWT Token Lifetimes (seconds)
```bash
export JWT_ACCESS_TOKEN_EXPIRES=900      # 15 minutes
export JWT_REFRESH_TOKEN_EXPIRES=1209600 # 14 days
```

#### Email Configuration (Gmail Example)
```bash
export MAIL_SERVER="smtp.gmail.com"
export MAIL_PORT=587
export MAIL_USE_TLS=1
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"  # Gmail App Password, not regular password
export MAIL_DEFAULT_SENDER="your-email@gmail.com"
```

#### Other Settings
```bash
export UPLOAD_FOLDER="static/resumes"
export FRONTEND_URL="http://localhost:5173"
export RATELIMIT_ENABLED=false
export RATELIMIT_DEFAULT=0
```

### Gmail Setup for Email Verification

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password (not your regular Gmail password)

### Quick Setup Script

Use the provided `environ.sh` script:
```bash
cd backend/
source environ.sh
```

Then modify `environ.sh` with your actual values.

## Running the App

### Option 1: Docker Compose (Recommended)
```bash
docker compose up -d --build
```

This starts three services:
- `backend`: Flask app served by Gunicorn on port 5000 (internal)
- `nginx`: Serves the built frontend and proxies `/api` to the backend on port 80
- `db`: PostgreSQL 16 with a persisted Docker volume

Build all images (Docker will pull NGINX and Postgres automatically):
```bash
docker compose build --no-cache
```

Start (build if needed):
```bash
docker compose up -d --build
```

Apply DB migrations once services are up (inside backend container):
```bash
docker compose exec backend bash -lc "python -m flask --app app.wsgi:app db upgrade"
```

To rebuild the frontend after code changes:
```bash
docker compose build nginx && docker compose up -d
```

Environment variables can be supplied via a `.env` file in this directory to override defaults (e.g., `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`, email settings, `FRONTEND_URL`).

Postgres defaults (override in .env as needed):
```
POSTGRES_USER=jobboard
POSTGRES_PASSWORD=jobboard
POSTGRES_DB=jobboard
```
The backend default DB URL in compose is `postgresql+psycopg://jobboard:jobboard@db:5432/jobboard`.

#### Accessing the app and changing ports
- Default URL (from compose mapping `nginx` ports: `"80:80"`):
  - Frontend: `http://localhost`
  - API (proxied): `http://localhost/api`
- Change the host port by editing `docker-compose.yml` under `nginx`:
  - Example: `ports: ["8080:80"]` → visit `http://localhost:8080`
- Verify published ports and containers:
```bash
docker compose ps
```
- Tail logs:
```bash
docker compose logs -f nginx
docker compose logs -f backend
docker compose logs -f db
```

### Option 2: Local Development
```bash
cd backend/
source environ.sh  # or set environment variables manually
python run.py
```

In a separate terminal for the frontend:
```bash
cd frontend/
npm ci
npx playwright install  # optional: for e2e tests later
npm run dev
```

### Option 3: Flask CLI
```bash
cd backend/
source environ.sh
flask run
```

## Database Migrations

If you need to update the database schema:
```bash
cd backend/
source environ.sh
python -m flask --app run:app db migrate -m "description"
python -m flask --app run:app db upgrade
```

## Test Suite

Backend (pytest):
```bash
cd backend/
python -m pytest -q
```

Frontend (unit tests via Vitest):
```bash
cd frontend/
npm run test -- run
```

Frontend (Playwright e2e - requires frontend dev server running and optional backend):
```bash
cd frontend/
npx playwright install
npx playwright test
```

## Features Overview

- Admin
  - Dashboard metrics with live recent activity feed (`/api/admin/activity_recent`)
  - Manage Users list with detail view and admin edit (no verification)
  - Recruiter request review flow
- Candidates & Recruiters
  - Job browsing, applications, recruiter job management
- Profile Update (Users)
  - Edit username/email gated by a 6‑digit email verification code

## First-time Setup Notes

1. Ensure email settings are correct if you want to send verification codes (otherwise backend will silently skip send in dev).
2. Rate limits are relaxed in development via `RATELIMIT_ENABLED=false`. In production, limits are enforced; auth endpoints default to 20/hour per IP.
3. For Playwright e2e, the frontend runs on `http://localhost:5173` by default.
4. If using Docker, set env vars in compose or `.env` and expose ports 5000 (backend) and 5173 (frontend).

## API Endpoints (Highlights)

- Auth
  - `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
  - Profile update flow: `POST /api/auth/profile/update/request-code`, `POST /api/auth/profile/update/verify-code`, `PUT /api/auth/profile`
- Admin
  - Metrics: `GET /api/admin/metrics`
  - Users: `GET /api/admin/users`, `GET /api/admin/users/:id`, `PUT /api/admin/users/:id`
  - Recent activity: `GET /api/admin/activity_recent`
  - Recruiter requests: review endpoints

## Troubleshooting

- Playwright complains about browsers: run `npx playwright install`.
- Rate limit errors in dev: set `RATELIMIT_ENABLED=false` and restart backend.
- Email not sending: verify SMTP credentials or set `MAIL_SUPPRESS_SEND=1` for local testing.
- 502/404 via NGINX: ensure backend is healthy `docker compose logs backend` and SPA fallback exists; rebuild `nginx` service after frontend changes.