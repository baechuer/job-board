#!/usr/bin/env python3
"""
Script to create random job applications
"""

import os
import sys
import random
from datetime import datetime, UTC

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

def create_random_applications():
    """Create random job applications"""
    
    app = create_app()
    with app.app_context():
        # Get all candidates and jobs
        candidates = db.session.execute(
            db.select(User).join(UserRole).where(UserRole.role == 'candidate')
        ).scalars().all()
        jobs = db.session.execute(db.select(Job)).scalars().all()
        
        if not candidates or not jobs:
            print('No candidates or jobs found')
            return
        
        print(f'Found {len(candidates)} candidates and {len(jobs)} jobs')
        
        # Sample application data
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Chris', 'Emma', 'Alex', 'Maria', 'Tom', 'Anna', 'Ben', 'Kate', 'Sam']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Wilson', 'Anderson', 'Taylor', 'Thomas', 'Jackson']
        companies = ['Tech Corp', 'Innovation Inc', 'StartupXYZ', 'BigTech Co', 'Dev Solutions', 'Code Masters', 'Software Plus', 'Tech Innovations', 'Cloud Systems', 'Data Analytics']
        positions = ['Software Engineer', 'Developer', 'Programmer', 'Software Developer', 'Full Stack Developer', 'Frontend Developer', 'Backend Developer', 'DevOps Engineer', 'Data Engineer']
        experiences = ['1-2 years', '2-3 years', '3-5 years', '5-7 years', '7+ years']
        educations = ['high_school', 'associate', 'bachelor', 'master', 'phd']
        skills_list = [
            'Python, JavaScript, React, Node.js',
            'Java, Spring Boot, MySQL, Docker',
            'C#, .NET, SQL Server, Azure',
            'JavaScript, TypeScript, Angular, MongoDB',
            'Python, Django, PostgreSQL, AWS',
            'React, Redux, Node.js, Express',
            'Vue.js, PHP, Laravel, MySQL',
            'Swift, iOS Development, Xcode',
            'Android, Kotlin, Java, Firebase',
            'Python, Machine Learning, TensorFlow',
            'Go, Kubernetes, Microservices, Docker'
        ]
        
        # Create 15-20 random applications
        num_applications = random.randint(15, 20)
        created_applications = []
        
        for i in range(num_applications):
            candidate = random.choice(candidates)
            job = random.choice(jobs)
            
            # Check if this candidate already applied to this job
            existing = db.session.execute(
                db.select(Application).where(
                    Application.user_id == candidate.id,
                    Application.job_id == job.id
                )
            ).scalar_one_or_none()
            
            if existing:
                continue
                
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            application = Application(
                user_id=candidate.id,
                job_id=job.id,
                first_name=first_name,
                last_name=last_name,
                email=f'{first_name.lower()}.{last_name.lower()}@example.com',
                phone=f'{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                current_company=random.choice(companies),
                current_position=random.choice(positions),
                experience=random.choice(experiences),
                education=random.choice(educations),
                skills=random.choice(skills_list),
                portfolio=f'https://{first_name.lower()}{last_name.lower()}.com',
                linkedin=f'https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}',
                github=f'https://github.com/{first_name.lower()}{last_name.lower()}',
                availability='Immediately',
                salary_expectation=random.randint(50000, 120000),
                notice_period=f'{random.randint(1, 4)} weeks',
                work_authorization='US Citizen',
                relocation=random.choice(['Yes', 'No']),
                additional_info=f'Passionate {random.choice(positions).lower()} with strong problem-solving skills.',
                status='submitted',
                resume_path=f'resumes/{first_name.lower()}_{last_name.lower()}_resume.pdf',
                cover_letter_path=f'cover_letters/{first_name.lower()}_{last_name.lower()}_cover_letter.pdf',
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            
            db.session.add(application)
            created_applications.append(f'{first_name} {last_name} -> {job.title}')
        
        db.session.commit()
        
        print(f'✅ Successfully created {len(created_applications)} job applications!')
        print('\n📋 Applications created:')
        for app in created_applications:
            print(f'   - {app}')

if __name__ == '__main__':
    create_random_applications()
