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

### Option 2: Local Development
```bash
cd backend/
source environ.sh  # or set environment variables manually
python run.py
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