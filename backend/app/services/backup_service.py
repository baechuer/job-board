"""
Database backup and recovery service
"""
import os
import shutil
import gzip
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class DatabaseBackupService:
    """Service for database backup and recovery operations"""
    
    def __init__(self):
        self.backup_dir = Path(current_app.instance_path) / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, backup_name=None):
        """Create a backup of the database"""
        try:
            # Get database path
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if not os.path.isabs(db_path):
                    db_path = os.path.join(current_app.instance_path, db_path)
            else:
                raise ValueError("Backup only supported for SQLite databases")
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found: {db_path}")
            
            # Generate backup filename
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_path = self.backup_dir / f"{backup_name}.db"
            compressed_path = self.backup_dir / f"{backup_name}.db.gz"
            
            # Create backup
            shutil.copy2(db_path, backup_path)
            
            # Compress backup
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            backup_path.unlink()
            
            logger.info(f"Database backup created: {compressed_path}")
            return str(compressed_path)
            
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            raise
    
    def restore_backup(self, backup_path):
        """Restore database from backup"""
        try:
            # Get database path
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if not os.path.isabs(db_path):
                    db_path = os.path.join(current_app.instance_path, db_path)
            else:
                raise ValueError("Restore only supported for SQLite databases")
            
            backup_path = Path(backup_path)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Create backup of current database before restore
            if os.path.exists(db_path):
                current_backup = self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                logger.info(f"Created pre-restore backup: {current_backup}")
            
            # Decompress and restore
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, db_path)
            
            logger.info(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            raise
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for backup_file in self.backup_dir.glob("*.db.gz"):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.stem.replace('.db', ''),
                'path': str(backup_file),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime)
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Remove backups older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_count = 0
        
        for backup_file in self.backup_dir.glob("*.db.gz"):
            if datetime.fromtimestamp(backup_file.stat().st_ctime) < cutoff_date:
                backup_file.unlink()
                removed_count += 1
                logger.info(f"Removed old backup: {backup_file}")
        
        logger.info(f"Cleaned up {removed_count} old backups")
        return removed_count
    
    def verify_backup(self, backup_path):
        """Verify that a backup file is valid"""
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                return False, "Backup file not found"
            
            # Try to open and read the backup
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rb') as f:
                    # Read first few bytes to check if it's a valid SQLite file
                    header = f.read(16)
                    if not header.startswith(b'SQLite format 3'):
                        return False, "Invalid SQLite backup file"
            else:
                with open(backup_path, 'rb') as f:
                    header = f.read(16)
                    if not header.startswith(b'SQLite format 3'):
                        return False, "Invalid SQLite backup file"
            
            return True, "Backup file is valid"
            
        except Exception as e:
            return False, f"Error verifying backup: {e}"

def create_backup_command():
    """Flask CLI command to create backup"""
    from flask.cli import with_appcontext
    
    @with_appcontext
    def create_backup():
        """Create a database backup"""
        try:
            backup_service = DatabaseBackupService()
            backup_path = backup_service.create_backup()
            print(f"✅ Backup created successfully: {backup_path}")
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return 1
    
    return create_backup

def restore_backup_command():
    """Flask CLI command to restore backup"""
    from flask.cli import with_appcontext
    import click
    
    @with_appcontext
    @click.argument('backup_path')
    def restore_backup(backup_path):
        """Restore database from backup"""
        try:
            backup_service = DatabaseBackupService()
            backup_service.restore_backup(backup_path)
            print(f"✅ Database restored successfully from: {backup_path}")
        except Exception as e:
            print(f"❌ Failed to restore backup: {e}")
            return 1
    
    return restore_backup

def list_backups_command():
    """Flask CLI command to list backups"""
    from flask.cli import with_appcontext
    
    @with_appcontext
    def list_backups():
        """List all available backups"""
        try:
            backup_service = DatabaseBackupService()
            backups = backup_service.list_backups()
            
            if not backups:
                print("No backups found")
                return
            
            print(f"{'Name':<30} {'Size':<10} {'Created':<20}")
            print("-" * 60)
            for backup in backups:
                size_mb = backup['size'] / (1024 * 1024)
                print(f"{backup['name']:<30} {size_mb:.2f}MB {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                
        except Exception as e:
            print(f"❌ Failed to list backups: {e}")
            return 1
    
    return list_backups
