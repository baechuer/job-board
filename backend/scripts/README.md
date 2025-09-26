# Scripts Directory

This directory contains utility scripts organized by functionality.

## Applications Scripts (`applications/`)

- `add_applications.py` - Add job applications to the database
- `create_applications.py` - Create sample job applications
- `manual_applications.py` - Manual application management

**Usage:** Run these scripts from the backend root directory:
```bash
python scripts/applications/add_applications.py
```

## Security Scripts (`security/`)

- `run_security_tests.py` - Run comprehensive security tests
- `setup_security.bat` - Windows security setup script
- `setup_security.sh` - Unix/Linux security setup script

**Usage:** Run these scripts from the backend root directory:
```bash
python scripts/security/run_security_tests.py
```

## Notes

- All scripts expect to be run from the backend root directory (`flask-framework/job-board/backend/`)
- Application scripts require the Flask app context and database
- Security scripts are standalone and can be run independently
