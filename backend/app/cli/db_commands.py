"""
Flask CLI commands for database management
"""
from flask.cli import AppGroup
from app.services.backup_service import (
    create_backup_command, 
    restore_backup_command, 
    list_backups_command
)

# Create CLI group for database operations
db_cli = AppGroup('db')

# Add backup commands
db_cli.command('backup')(create_backup_command())
db_cli.command('restore')(restore_backup_command())
db_cli.command('list-backups')(list_backups_command())

def init_db_commands(app):
    """Initialize database CLI commands"""
    app.cli.add_command(db_cli)
