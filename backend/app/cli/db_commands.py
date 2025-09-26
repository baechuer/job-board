"""
Flask CLI commands for database management
"""
from flask.cli import AppGroup
from app.services.backup_service import (
    create_backup_command, 
    restore_backup_command, 
    list_backups_command
)

# Create CLI group for backup operations (avoid clashing with Flask-Migrate 'db')
backup_cli = AppGroup('backup')

# Add backup commands
backup_cli.command('create')(create_backup_command())
backup_cli.command('restore')(restore_backup_command())
backup_cli.command('list')(list_backups_command())

def init_db_commands(app):
    """Initialize backup CLI commands and keep Flask-Migrate 'db' group intact"""
    app.cli.add_command(backup_cli)
