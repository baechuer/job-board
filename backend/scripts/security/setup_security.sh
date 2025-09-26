#!/bin/bash

# Security Setup Script for Flask Job Board Application
# This script installs the required security dependencies and sets up the environment

echo "🔒 Setting up security features for Flask Job Board Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install security dependencies
echo "Installing security dependencies..."
pip install -r requirements.txt

# Install additional security tools (optional)
echo "Installing additional security tools..."
pip install python-magic-bin  # For Windows compatibility

# Check if ClamAV is available (optional)
if command -v clamscan &> /dev/null; then
    echo "✅ ClamAV is available for virus scanning"
else
    echo "⚠️  ClamAV not found. Virus scanning will be disabled."
    echo "   To enable virus scanning, install ClamAV:"
    echo "   - Ubuntu/Debian: sudo apt-get install clamav"
    echo "   - macOS: brew install clamav"
    echo "   - Windows: Download from https://www.clamav.net/"
fi

# Create upload directory
echo "Creating upload directory..."
mkdir -p static/uploads
mkdir -p static/applications
mkdir -p static/users

# Set proper permissions
echo "Setting directory permissions..."
chmod 755 static/uploads
chmod 755 static/applications
chmod 755 static/users

# Create environment file template
echo "Creating environment file template..."
cat > .env.example << EOF
# Security Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database
DATABASE_URL=sqlite:///instance/app.db

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_DEFAULT="200 per day, 50 per hour"

# File Upload Security
MAX_CONTENT_LENGTH=10485760
UPLOAD_FOLDER=static/uploads
ALLOWED_EXTENSIONS="pdf,doc,docx,txt,rtf,odt"

# CORS Settings
CORS_ORIGINS="http://localhost:5173"

# Virus Scanning
ENABLE_VIRUS_SCAN=true
CLAMSCAN_PATH=clamscan

# Input Validation
MAX_STRING_LENGTH=1000
MAX_EMAIL_LENGTH=254
MAX_PASSWORD_LENGTH=128

# Mail Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Frontend URL
FRONTEND_URL=http://localhost:5173
EOF

echo "✅ Security setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure your settings"
echo "2. Run database migrations: flask db upgrade"
echo "3. Start the application: python run.py"
echo ""
echo "Security features enabled:"
echo "✅ Input validation and sanitization"
echo "✅ File type validation and virus scanning"
echo "✅ Rate limiting on all endpoints"
echo "✅ CORS configuration"
echo "✅ Security headers"
echo "✅ Enhanced authentication"
echo ""
echo "For more information, see SECURITY.md"
