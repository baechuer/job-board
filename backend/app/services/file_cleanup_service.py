import os
import shutil
from pathlib import Path
from typing import List, Optional
from flask import current_app
from ..extensions import db
from ..models.application import Application
from ..models.job import Job
from ..models.saved_job import SavedJob
from sqlalchemy import select


class FileCleanupService:
    """Service for cleaning up files and folders when jobs are deleted"""
    
    def __init__(self):
        # Handle both test and production environments
        if hasattr(current_app, 'instance_path') and current_app.instance_path:
            self.static_folder = Path(current_app.instance_path).parent / 'static'
        else:
            # Fallback for testing or when instance_path is not set
            self.static_folder = Path(__file__).parent.parent.parent / 'static'
    
    def cleanup_job_files(self, job_id: int) -> dict:
        """
        Clean up all files and folders associated with a job deletion.
        This includes:
        - All application files (resumes, cover letters)
        - User-specific folders if empty
        - Job-specific folders
        
        Returns:
            dict: Cleanup summary with counts and paths
        """
        cleanup_summary = {
            'files_deleted': 0,
            'folders_deleted': 0,
            'errors': [],
            'deleted_paths': []
        }
        
        try:
            # Get all applications for this job
            applications = db.session.execute(
                select(Application).where(Application.job_id == job_id)
            ).scalars().all()
            
            # Track user folders to potentially clean up
            user_folders_to_check = set()
            
            # Delete application files
            for application in applications:
                user_folders_to_check.add(application.user_id)
                
                # Delete resume file
                if application.resume_path:
                    resume_path = self.static_folder / application.resume_path
                    if self._delete_file(resume_path):
                        cleanup_summary['files_deleted'] += 1
                        cleanup_summary['deleted_paths'].append(str(resume_path))
                
                # Delete cover letter file
                if application.cover_letter_path:
                    cover_letter_path = self.static_folder / application.cover_letter_path
                    if self._delete_file(cover_letter_path):
                        cleanup_summary['files_deleted'] += 1
                        cleanup_summary['deleted_paths'].append(str(cover_letter_path))
            
            # Clean up empty user folders
            for user_id in user_folders_to_check:
                user_folder = self.static_folder / 'applications' / str(user_id)
                if self._cleanup_empty_folder(user_folder):
                    cleanup_summary['folders_deleted'] += 1
                    cleanup_summary['deleted_paths'].append(str(user_folder))
            
            # Clean up job-specific folder if it exists
            job_folder = self.static_folder / 'jobs' / str(job_id)
            if self._cleanup_empty_folder(job_folder):
                cleanup_summary['folders_deleted'] += 1
                cleanup_summary['deleted_paths'].append(str(job_folder))
            
        except Exception as e:
            cleanup_summary['errors'].append(f"Error during cleanup: {str(e)}")
            current_app.logger.error(f"File cleanup error for job {job_id}: {str(e)}")
        
        return cleanup_summary
    
    def cleanup_user_files(self, user_id: int) -> dict:
        """
        Clean up all files associated with a user deletion.
        This includes all their application files and folders.
        """
        cleanup_summary = {
            'files_deleted': 0,
            'folders_deleted': 0,
            'errors': [],
            'deleted_paths': []
        }
        
        try:
            # Get all applications for this user
            applications = db.session.execute(
                select(Application).where(Application.user_id == user_id)
            ).scalars().all()
            
            # Delete all application files
            for application in applications:
                # Delete resume file
                if application.resume_path:
                    resume_path = self.static_folder / application.resume_path
                    if self._delete_file(resume_path):
                        cleanup_summary['files_deleted'] += 1
                        cleanup_summary['deleted_paths'].append(str(resume_path))
                
                # Delete cover letter file
                if application.cover_letter_path:
                    cover_letter_path = self.static_folder / application.cover_letter_path
                    if self._delete_file(cover_letter_path):
                        cleanup_summary['files_deleted'] += 1
                        cleanup_summary['deleted_paths'].append(str(cover_letter_path))
            
            # Clean up user folder
            user_folder = self.static_folder / 'applications' / str(user_id)
            if self._cleanup_empty_folder(user_folder):
                cleanup_summary['folders_deleted'] += 1
                cleanup_summary['deleted_paths'].append(str(user_folder))
            
        except Exception as e:
            cleanup_summary['errors'].append(f"Error during user cleanup: {str(e)}")
            current_app.logger.error(f"User file cleanup error for user {user_id}: {str(e)}")
        
        return cleanup_summary
    
    def _delete_file(self, file_path: Path) -> bool:
        """Safely delete a file if it exists"""
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                current_app.logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False
    
    def _cleanup_empty_folder(self, folder_path: Path) -> bool:
        """Safely delete an empty folder if it exists"""
        try:
            if folder_path.exists() and folder_path.is_dir():
                # Check if folder is empty
                if not any(folder_path.iterdir()):
                    folder_path.rmdir()
                    current_app.logger.info(f"Deleted empty folder: {folder_path}")
                    return True
            return False
        except Exception as e:
            current_app.logger.error(f"Failed to delete folder {folder_path}: {str(e)}")
            return False
    
    def cleanup_orphaned_files(self) -> dict:
        """
        Clean up orphaned files that don't have corresponding database records.
        This is useful for maintenance tasks.
        """
        cleanup_summary = {
            'files_deleted': 0,
            'folders_deleted': 0,
            'errors': [],
            'deleted_paths': []
        }
        
        try:
            # Get all application file paths from database
            applications = db.session.execute(select(Application)).scalars().all()
            valid_paths = set()
            
            for app in applications:
                if app.resume_path:
                    valid_paths.add(self.static_folder / app.resume_path)
                if app.cover_letter_path:
                    valid_paths.add(self.static_folder / app.cover_letter_path)
            
            # Scan applications folder for orphaned files
            applications_folder = self.static_folder / 'applications'
            if applications_folder.exists():
                for user_folder in applications_folder.iterdir():
                    if user_folder.is_dir():
                        for file_path in user_folder.rglob('*'):
                            if file_path.is_file() and file_path not in valid_paths:
                                if self._delete_file(file_path):
                                    cleanup_summary['files_deleted'] += 1
                                    cleanup_summary['deleted_paths'].append(str(file_path))
                        
                        # Clean up empty user folders
                        if self._cleanup_empty_folder(user_folder):
                            cleanup_summary['folders_deleted'] += 1
                            cleanup_summary['deleted_paths'].append(str(user_folder))
            
        except Exception as e:
            cleanup_summary['errors'].append(f"Error during orphaned file cleanup: {str(e)}")
            current_app.logger.error(f"Orphaned file cleanup error: {str(e)}")
        
        return cleanup_summary
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics for the static folder"""
        stats = {
            'total_files': 0,
            'total_size_bytes': 0,
            'applications_folder_size': 0,
            'jobs_folder_size': 0,
            'other_files_size': 0
        }
        
        try:
            if self.static_folder.exists():
                for file_path in self.static_folder.rglob('*'):
                    if file_path.is_file():
                        file_size = file_path.stat().st_size
                        stats['total_files'] += 1
                        stats['total_size_bytes'] += file_size
                        
                        # Categorize by folder
                        relative_path = file_path.relative_to(self.static_folder)
                        if len(relative_path.parts) > 0 and relative_path.parts[0] == 'applications':
                            stats['applications_folder_size'] += file_size
                        elif len(relative_path.parts) > 0 and relative_path.parts[0] == 'jobs':
                            stats['jobs_folder_size'] += file_size
                        else:
                            stats['other_files_size'] += file_size
            
        except Exception as e:
            current_app.logger.error(f"Error getting storage stats: {str(e)}")
        
        return stats
