# Job-Board – Technical Review, Architecture, and Interview Notes

## 1) High-level Purpose and Product Story
Job Board is a full‑stack recruiting platform enabling:
- Candidates to discover jobs and apply with documents
- Recruiters to create/manage jobs and review applications
- Admins to supervise users and approve recruiter access

It deploys as a single-origin site (NGINX serves the SPA and reverse‑proxies `/api` to Flask), avoiding browser CORS complexity in production.

## 2) System Architecture
- Frontend: React (Vite), Tailwind, React Router, React Query
- Backend: Flask + SQLAlchemy + Marshmallow + JWT, Gunicorn in prod
- Database: PostgreSQL (Docker service) or managed DB
- Reverse Proxy: NGINX serves built SPA and proxies `/api/*` → backend
- Auth: JWT access + refresh tokens; role claims (admin, recruiter, candidate)
- Rate Limiting: Flask‑Limiter (disabled in dev; configurable via env)
- Testing: pytest (backend), Vitest (frontend), Playwright (e2e optional)
- Containers: docker‑compose orchestrates `nginx`, `backend`, and `db`

### 2.1 Component Diagram (conceptual)
SPA (React) → NGINX (static + reverse proxy) → Flask (Gunicorn) → Postgres

### 2.2 Runtime Flow (happy path)
1. User hits `http://localhost` → NGINX returns SPA index and assets
2. SPA calls `/api/auth/login`/`/api/auth/register` (NGINX forwards to Flask)
3. Flask authenticates, returns JWT access/refresh
4. SPA stores tokens (localStorage) and makes authenticated calls
5. DB operations via SQLAlchemy; Marshmallow validates payloads

## 3) Domain Model (key entities)
- User(id, email, username, password_hash, is_verified, roles[UserRole])
- UserRole(user_id, role[admin|recruiter|candidate])
- Job(id, user_id(owner), title, description, salary_min/max, location, etc.)
- Application(id, job_id, submitter details, resume/cover paths, status)
- RecruiterRequest(id, user_id, status, notes)
- VerificationCode(user_id, code, purpose=profile_update, expires_at, consumed_at)

## 4) Core Workflows (detailed)
### 4.1 Authentication
- Register → strong password checks (min 8, uppercase, lowercase, digit, special)
- Login → JWT access + refresh; `GET /api/auth/me` returns user + roles
- Refresh → issues short‑lived access token; logout revokes token (per‑device)

### 4.2 Admin
- Dashboard: `/api/admin/metrics`, `/api/admin/activity_recent`
- Users: `/api/admin/users`, detail `GET/PUT /api/admin/users/:id` (no code)
- Recruiter Requests: list + approve/reject endpoints

### 4.3 Recruiter
- Create job, view "My Jobs", per‑job applications, application detail

### 4.4 Candidate
- Browse jobs; submit application (resume + cover letter validated)
- Profile edit requires 6‑digit verification via email

## 5) Key Design Decisions
- Single origin via NGINX
  - Pros: no CORS; CDN‑friendly; one public endpoint
  - Cons: adds reverse proxy management and build step
- JWT Auth with roles
  - Pros: stateless, scalable; works well behind proxies
  - Cons: token storage on client demands careful handling; need revocation
- SQLAlchemy + Postgres
  - Pros: robust relational model, migrations, enums, constraints
  - Cons: migrations and enum evolution require discipline
- Email‑code verification for sensitive profile changes
  - Pros: better account security, no password re‑entry
  - Cons: requires email deliverability; user friction

## 6) Deployment Model
- docker‑compose services:
  - `nginx`: serves `frontend/dist`, proxies `/api` → `backend:5000`
  - `backend`: Gunicorn application server
  - `db`: Postgres with a persistent Docker volume `db_data`
- Env‑based admin seeding (on boot): `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_USERNAME`

## 7) API Surface (selected)
- Auth: `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/refresh`
- Profile update: `POST /api/auth/profile/update/request-code`, `POST /api/auth/profile/update/verify-code`, `PUT /api/auth/profile`
- Admin: `GET /api/admin/metrics`, `GET /api/admin/activity_recent`, `GET/PUT /api/admin/users/:id`, `GET /api/admin/users`
- Recruiter requests: `GET /api/admin/recruiter-requests`, `PUT .../approve`, `PUT .../reject`
- Recruiter jobs: `/api/recruiter/*`
- Applications: `/api/applications/*`

## 8) Observed Strengths
- Solid layering: schemas → services → API → gateway (NGINX)
- Clear role separation and RBAC at endpoints
- Good DX: tests (unit/integration) and Playwright mocks
- Security touches: strong password policy, token revocation, attachment scanning stubs, email verification for profile changes
- Dockerized with a clean reverse‑proxy front

## 9) Known Issues / Critique & Remedies
- Rate‑limit warnings in dev
  - Cause: limiter initializes without storage string and logs warnings; RATELIMIT_DEFAULT was invalid previously
  - Fix: set `RATELIMIT_STORAGE_URL=memory://` and keep `RATELIMIT_ENABLED=false` in dev to silence warnings cleanly
- Initial Postgres enum race logs
  - Cause: enum creation when multiple workers start simultaneously
  - Fix: standardize on migrations and remove any auto‑create race paths; consider booting with 1 worker the first time
- Frontend AbortSignal leakage
  - Issue: `signal` leaked into query params causing 400s
  - Fix: pass `signal` as axios option: `api.get(url, { params, signal })`
- E2E tests reliance on running backend
  - Improve by mocking network for most flows; reserve live E2E for a smaller happy‑path suite
- Email delivery
  - In dev, emails are often suppressed; document expectations and provide dev mailbox (MailHog) via compose for testing
- Static file security
  - Ensure NGINX only serves known SPA assets; verify headers (CSP, HSTS) as appropriate for prod

## 10) Alternatives Considered
- Serving SPA from Flask instead of NGINX
  - Simpler containers but less optimal static serving & caching
- Session‑based auth instead of JWT
  - Easier logout semantics; tighter CSRF protection built‑in, but more stateful and trickier for API clients
- ORM alternatives (e.g., Prisma via Node) or document stores
  - Different tradeoffs; SQL with SQLAlchemy is a good fit for relational recruiting data
- Fully managed hosting (Cloud Run + Cloud SQL + Cloud Storage + CDN)
  - Reduces ops burden; requires IaC and cloud‑native routing (Ingress/ALB) setup

## 11) Operational Guidelines
- Migrations
  - Recommended: `flask db upgrade` upon deploy (compose exec) or auto‑migrate entrypoint
- Admin seeding
  - Use `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_USERNAME` envs
- Logs & health
  - `/health` endpoint (simple JSON), `docker compose logs -f` for services
- Security
  - Keep secrets out of images; use env or secrets manager
  - Consider Redis for rate limiting storage in prod

## 12) Interview Talking Points
- Why single-origin with NGINX proxy
- Role‑based auth in JWT and revocation strategy
- Input validation stack (Marshmallow; strong password; file checks)
- Testing strategy and mocking approach
- Migration strategy and first‑run DB setup
- Observability plan (structured logs, health endpoints)

## 13) Immediate Improvements (Actionable)
- Wire an auto‑migrate entrypoint to run `db upgrade` before Gunicorn starts
- Add Redis to compose and configure `RATELIMIT_STORAGE_URL=redis://redis:6379`
- Add MailHog service for local email testing; point MAIL_* to it in dev
- Harden NGINX headers (CSP, HSTS where TLS terminates) and disable directory listings
- Add pagination/sorting controls to admin tables and consistent empty‑states
- CI job: run pytest + vitest on PR; optional Playwright smoke

---
Exporting this doc
- Open this file and print to PDF in your editor or use Pandoc:
  - `pandoc docs/JobBoard_TechReview.md -o JobBoard_TechReview.pdf`
