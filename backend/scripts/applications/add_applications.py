#!/usr/bin/env python3
"""
Simple script to add job applications
"""

import os
import sys
# Add the backend root directory to the path so we can import app
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels: scripts/applications -> scripts -> backend
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.user_role import UserRole

def add_applications():
    """Add job applications"""
    
    app = create_app()
    with app.app_context():
        # Get first candidate user
        candidate = db.session.execute(
            db.select(User).join(UserRole).where(UserRole.role == 'candidate').limit(1)
        ).scalar_one_or_none()
        
        if not candidate:
            print("No candidate found!")
            return
        
        # Get all jobs
        jobs = db.session.execute(db.select(Job)).scalars().all()
        
        if not jobs:
            print("No jobs found!")
            return
        
        print(f"Found candidate: {candidate.email}")
        print(f"Found {len(jobs)} jobs")
        
        # Create applications for first 3 jobs
        applications_created = 0
        for i, job in enumerate(jobs[:3]):
            # Check if application already exists
            existing = db.session.execute(
                db.select(Application).where(
                    Application.user_id == candidate.id,
                    Application.job_id == job.id
                )
            ).scalar_one_or_none()
            
            if existing:
                print(f"Application already exists for job {job.id}")
                continue
            
            # Create application
            application = Application(
                user_id=candidate.id,
                job_id=job.id,
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone="123-456-7890",
                current_company="Tech Corp",
                current_position="Software Engineer",
                experience="3-5 years",
                education="Bachelor of Computer Science",
                skills="React, Node.js, Python",
                portfolio="https://johndoe.dev",
                linkedin="https://linkedin.com/in/johndoe",
                github="https://github.com/johndoe",
                availability="Immediate",
                salary_expectation="70000",
                notice_period="2 weeks",
                work_authorization="Yes",
                relocation="No",
                additional_info="Passionate developer with strong technical skills",
                status="submitted",
                resume_path="applications/1/resume.pdf",
                cover_letter_path="applications/1/cover.pdf"
            )
            
            db.session.add(application)
            applications_created += 1
            print(f"Created application for job: {job.title}")
        
        db.session.commit()
        print(f"Successfully created {applications_created} applications!")

if __name__ == "__main__":
    add_applications()
