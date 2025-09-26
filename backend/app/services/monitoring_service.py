"""
Database monitoring and health check service
"""
import os
import time
import logging
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

logger = logging.getLogger(__name__)

class DatabaseMonitor:
    """Database monitoring and health check service"""
    
    def __init__(self):
        self.health_history = []
        self.max_history = 100
    
    def check_database_health(self):
        """Perform comprehensive database health check"""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        try:
            # Check database connection
            connection_check = self._check_connection()
            health_status['checks']['connection'] = connection_check
            
            # Check database size
            size_check = self._check_database_size()
            health_status['checks']['database_size'] = size_check
            
            # Check table integrity
            integrity_check = self._check_table_integrity()
            health_status['checks']['table_integrity'] = integrity_check
            
            # Check connection pool status
            pool_check = self._check_connection_pool()
            health_status['checks']['connection_pool'] = pool_check
            
            # Check for long-running queries
            query_check = self._check_long_running_queries()
            health_status['checks']['long_queries'] = query_check
            
            # Determine overall status
            failed_checks = [check for check in health_status['checks'].values() 
                           if not check.get('status', True)]
            if failed_checks:
                health_status['overall_status'] = 'unhealthy'
                health_status['failed_checks'] = [check['name'] for check in failed_checks]
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status['overall_status'] = 'error'
            health_status['error'] = str(e)
        
        # Store in history
        self.health_history.append(health_status)
        if len(self.health_history) > self.max_history:
            self.health_history.pop(0)
        
        return health_status
    
    def _check_connection(self):
        """Check database connection"""
        try:
            start_time = time.time()
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            response_time = (time.time() - start_time) * 1000
            
            return {
                'name': 'connection',
                'status': True,
                'response_time_ms': round(response_time, 2),
                'message': 'Database connection successful'
            }
        except SQLAlchemyError as e:
            return {
                'name': 'connection',
                'status': False,
                'error': str(e),
                'message': 'Database connection failed'
            }
    
    def _check_database_size(self):
        """Check database size"""
        try:
            # Get database file size for SQLite
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if not os.path.isabs(db_path):
                    db_path = os.path.join(current_app.instance_path, db_path)
                
                size_bytes = os.path.getsize(db_path)
                size_mb = size_bytes / (1024 * 1024)
                
                # Warning if database is larger than 100MB
                status = size_mb < 100
                
                return {
                    'name': 'database_size',
                    'status': status,
                    'size_mb': round(size_mb, 2),
                    'size_bytes': size_bytes,
                    'message': f'Database size: {size_mb:.2f}MB',
                    'warning': 'Database size exceeds 100MB' if not status else None
                }
            else:
                return {
                    'name': 'database_size',
                    'status': True,
                    'message': 'Database size check not supported for this database type'
                }
        except Exception as e:
            return {
                'name': 'database_size',
                'status': False,
                'error': str(e),
                'message': 'Failed to check database size'
            }
    
    def _check_table_integrity(self):
        """Check table integrity"""
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            integrity_issues = []
            for table in tables:
                try:
                    # Check if table can be queried
                    with db.engine.connect() as conn:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                except Exception as e:
                    integrity_issues.append(f"Table {table}: {str(e)}")
            
            status = len(integrity_issues) == 0
            
            return {
                'name': 'table_integrity',
                'status': status,
                'tables_checked': len(tables),
                'issues': integrity_issues,
                'message': f'Checked {len(tables)} tables, {len(integrity_issues)} issues found'
            }
        except Exception as e:
            return {
                'name': 'table_integrity',
                'status': False,
                'error': str(e),
                'message': 'Failed to check table integrity'
            }
    
    def _check_connection_pool(self):
        """Check connection pool status"""
        try:
            pool = db.engine.pool
            
            # Get basic pool information
            pool_info = {
                'name': 'connection_pool',
                'status': True,
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'message': f'Pool: {pool.checkedin()}/{pool.size()} available'
            }
            
            # Try to get invalid count if available
            try:
                pool_info['invalid'] = pool.invalid()
            except AttributeError:
                pool_info['invalid'] = 'N/A'
                pool_info['note'] = 'Invalid count not available for this pool type'
            
            return pool_info
        except Exception as e:
            return {
                'name': 'connection_pool',
                'status': False,
                'error': str(e),
                'message': 'Failed to check connection pool'
            }
    
    def _check_long_running_queries(self):
        """Check for long-running queries (SQLite doesn't support this well)"""
        try:
            # For SQLite, we can't easily check running queries
            # This is more relevant for PostgreSQL/MySQL
            return {
                'name': 'long_queries',
                'status': True,
                'message': 'Long query check not supported for SQLite',
                'note': 'Consider upgrading to PostgreSQL for production monitoring'
            }
        except Exception as e:
            return {
                'name': 'long_queries',
                'status': False,
                'error': str(e),
                'message': 'Failed to check long-running queries'
            }
    
    def get_health_history(self, hours=24):
        """Get health check history for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [check for check in self.health_history 
                if datetime.fromisoformat(check['timestamp']) > cutoff_time]
    
    def get_health_summary(self):
        """Get health check summary"""
        if not self.health_history:
            return {'status': 'no_data', 'message': 'No health checks performed yet'}
        
        recent_checks = self.get_health_history(hours=1)
        if not recent_checks:
            return {'status': 'stale', 'message': 'No recent health checks'}
        
        healthy_count = sum(1 for check in recent_checks if check['overall_status'] == 'healthy')
        total_count = len(recent_checks)
        
        return {
            'status': 'healthy' if healthy_count == total_count else 'unhealthy',
            'healthy_checks': healthy_count,
            'total_checks': total_count,
            'success_rate': round((healthy_count / total_count) * 100, 2),
            'last_check': recent_checks[-1]['timestamp'] if recent_checks else None
        }

# Global monitor instance
db_monitor = DatabaseMonitor()

def get_database_health():
    """Get current database health status"""
    return db_monitor.check_database_health()

def get_health_summary():
    """Get database health summary"""
    return db_monitor.get_health_summary()
