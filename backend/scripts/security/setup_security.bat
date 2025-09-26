@echo off
REM Security Setup Script for Flask Job Board Application (Windows)
REM This script installs the required security dependencies and sets up the environment

echo 🔒 Setting up security features for Flask Job Board Application...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install security dependencies
echo Installing security dependencies...
pip install -r requirements.txt

REM Install additional security tools (optional)
echo Installing additional security tools...
pip install python-magic-bin

REM Check if ClamAV is available (optional)
where clamscan >nul 2>nul
if %errorlevel% == 0 (
    echo ✅ ClamAV is available for virus scanning
) else (
    echo ⚠️  ClamAV not found. Virus scanning will be disabled.
    echo    To enable virus scanning, install ClamAV:
    echo    - Download from https://www.clamav.net/
    echo    - Or use Windows Subsystem for Linux (WSL)
)

REM Create upload directory
echo Creating upload directory...
if not exist "static\uploads" mkdir static\uploads
if not exist "static\applications" mkdir static\applications
if not exist "static\users" mkdir static\users

REM Create environment file template
echo Creating environment file template...
(
echo # Security Configuration
echo SECRET_KEY=your-secret-key-here
echo JWT_SECRET_KEY=your-jwt-secret-key-here
echo.
echo # Database
echo DATABASE_URL=sqlite:///instance/app.db
echo.
echo # Rate Limiting
echo RATELIMIT_STORAGE_URL=memory://
echo RATELIMIT_DEFAULT="200 per day, 50 per hour"
echo.
echo # File Upload Security
echo MAX_CONTENT_LENGTH=10485760
echo UPLOAD_FOLDER=static/uploads
echo ALLOWED_EXTENSIONS="pdf,doc,docx,txt,rtf,odt"
echo.
echo # CORS Settings
echo CORS_ORIGINS="http://localhost:5173"
echo.
echo # Virus Scanning
echo ENABLE_VIRUS_SCAN=true
echo CLAMSCAN_PATH=clamscan
echo.
echo # Input Validation
echo MAX_STRING_LENGTH=1000
echo MAX_EMAIL_LENGTH=254
echo MAX_PASSWORD_LENGTH=128
echo.
echo # Mail Configuration
echo MAIL_SERVER=smtp.gmail.com
echo MAIL_PORT=587
echo MAIL_USE_TLS=1
echo MAIL_USERNAME=your-email@gmail.com
echo MAIL_PASSWORD=your-app-password
echo.
echo # Frontend URL
echo FRONTEND_URL=http://localhost:5173
) > .env.example

echo ✅ Security setup complete!
echo.
echo Next steps:
echo 1. Copy .env.example to .env and configure your settings
echo 2. Run database migrations: flask db upgrade
echo 3. Start the application: python run.py
echo.
echo Security features enabled:
echo ✅ Input validation and sanitization
echo ✅ File type validation and virus scanning
echo ✅ Rate limiting on all endpoints
echo ✅ CORS configuration
echo ✅ Security headers
echo ✅ Enhanced authentication
echo.
echo For more information, see SECURITY.md

pause
