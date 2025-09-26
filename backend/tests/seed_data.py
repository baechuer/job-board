#!/usr/bin/env python3
"""
Data seeding script to recreate realistic test data
Run this to populate the database with users and jobs
"""

import os
import sys

# Add the parent directory to the path so we can import app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.user_role import UserRole
from app.common.security import hash_password
from datetime import date, datetime, UTC
import random
import os
from pathlib import Path
from flask import current_app
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def create_users_and_jobs(clear_existing=False):
    """Create realistic users and jobs"""
    
    app = create_app()
    with app.app_context():
        # Only clear existing data if explicitly requested
        if clear_existing:
            print("Clearing existing data...")
            db.session.query(Application).delete()
            db.session.query(UserRole).delete()
            db.session.query(Job).delete()
            db.session.query(User).delete()
            db.session.commit()
        else:
            print("Adding data to existing database (use --clear to clear existing data)...")
        
        # Sample users data - baechuer1 to baechuer4 with different roles
        users_data = [
            {
                'email': 'baechuer1@gmail.com',
                'username': 'baechuer1',
                'password': 'Password123',
                'roles': ['admin'],
                'is_verified': True
            },
            {
                'email': 'baechuer2@gmail.com',
                'username': 'baechuer2',
                'password': 'Password123',
                'roles': ['recruiter'],
                'is_verified': True
            },
            {
                'email': 'baechuer3@gmail.com',
                'username': 'baechuer3',
                'password': 'Password123',
                'roles': ['candidate'],
                'is_verified': True
            },
            {
                'email': 'baechuer4@gmail.com',
                'username': 'baechuer4',
                'password': 'Password123',
                'roles': ['recruiter'],
                'is_verified': True
            }
        ]
        
        # Add additional candidate users for applications
        additional_candidates = [
            {
                'email': 'candidate1@gmail.com',
                'username': 'candidate1',
                'password': 'Password123',
                'roles': ['candidate'],
                'is_verified': True
            },
            {
                'email': 'candidate2@gmail.com',
                'username': 'candidate2',
                'password': 'Password123',
                'roles': ['candidate'],
                'is_verified': True
            },
            {
                'email': 'candidate3@gmail.com',
                'username': 'candidate3',
                'password': 'Password123',
                'roles': ['candidate'],
                'is_verified': True
            }
        ]
        
        users_data.extend(additional_candidates)
        
        # Create users
        print("Creating users...")
        created_users = {}
        for user_data in users_data:
            # Check if user already exists (only when not clearing)
            if not clear_existing:
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if existing_user:
                    print(f"User {user_data['email']} already exists, skipping...")
                    created_users[user_data['email']] = existing_user
                    continue
            
            # Hash password
            password_hash = hash_password(user_data['password'])
            
            user = User(
                email=user_data['email'],
                username=user_data['username'],
                password_hash=password_hash,
                is_verified=user_data['is_verified']
            )
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Add roles
            for role in user_data['roles']:
                user_role = UserRole(user_id=user.id, role=role)
                db.session.add(user_role)
            
            created_users[user_data['email']] = user
            print(f"Created user: {user_data['email']} ({user_data['roles']})")
        
        db.session.commit()
        
        # Random jobs data - distributed among recruiters (baechuer2 and baechuer4)
        jobs_data = [
            {
                'title': 'Senior Full Stack Developer',
                'description': 'We are looking for a senior full stack developer to lead our development team. You will work on both frontend and backend systems.',
                'salary_min': 120000,
                'salary_max': 180000,
                'location': 'San Francisco, CA',
                'requirements': ['React', 'Node.js', 'TypeScript', 'PostgreSQL', 'AWS'],
                'responsibilities': 'Lead development projects, mentor junior developers, architect scalable solutions',
                'skills': ['React', 'Node.js', 'TypeScript', 'PostgreSQL', 'AWS', 'Docker', 'GraphQL'],
                'employment_type': 'full_time',
                'work_mode': 'hybrid',
                'seniority': 'senior',
                'recruiter_email': 'baechuer2@gmail.com'
            },
            {
                'title': 'Frontend Engineer',
                'description': 'Join our frontend team to build modern, responsive web applications using React and modern JavaScript.',
                'salary_min': 85000,
                'salary_max': 125000,
                'location': 'New York, NY',
                'requirements': ['React', 'JavaScript', 'CSS', 'HTML5'],
                'responsibilities': 'Develop user interfaces, optimize performance, collaborate with designers',
                'skills': ['React', 'JavaScript', 'CSS3', 'HTML5', 'Webpack', 'Jest'],
                'employment_type': 'full_time',
                'work_mode': 'remote',
                'seniority': 'mid',
                'recruiter_email': 'baechuer4@gmail.com'
            },
            {
                'title': 'Backend API Developer',
                'description': 'We need a backend developer to build robust REST APIs and microservices using Python and cloud technologies.',
                'salary_min': 95000,
                'salary_max': 140000,
                'location': 'Seattle, WA',
                'requirements': ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
                'responsibilities': 'Design APIs, implement business logic, ensure scalability and security',
                'skills': ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'Redis', 'Celery'],
                'employment_type': 'full_time',
                'work_mode': 'onsite',
                'seniority': 'mid',
                'recruiter_email': 'baechuer2@gmail.com'
            },
            {
                'title': 'DevOps Engineer',
                'description': 'Join our DevOps team to manage cloud infrastructure and CI/CD pipelines. Kubernetes experience required.',
                'salary_min': 110000,
                'salary_max': 160000,
                'location': 'Austin, TX',
                'requirements': ['Kubernetes', 'AWS', 'Terraform', 'Jenkins'],
                'responsibilities': 'Manage infrastructure, automate deployments, monitor system health',
                'skills': ['Kubernetes', 'AWS', 'Terraform', 'Jenkins', 'Prometheus', 'Grafana'],
                'employment_type': 'full_time',
                'work_mode': 'remote',
                'seniority': 'senior',
                'recruiter_email': 'baechuer4@gmail.com'
            },
            {
                'title': 'Data Engineer',
                'description': 'We are looking for a data engineer to build and maintain our data pipelines and analytics infrastructure.',
                'salary_min': 100000,
                'salary_max': 150000,
                'location': 'Boston, MA',
                'requirements': ['Python', 'SQL', 'Apache Airflow', 'BigQuery'],
                'responsibilities': 'Build data pipelines, optimize queries, maintain data warehouse',
                'skills': ['Python', 'SQL', 'Apache Airflow', 'BigQuery', 'dbt', 'Snowflake'],
                'employment_type': 'full_time',
                'work_mode': 'hybrid',
                'seniority': 'senior',
                'recruiter_email': 'baechuer2@gmail.com'
            },
            {
                'title': 'Mobile App Developer',
                'description': 'Develop cross-platform mobile applications using React Native. iOS and Android experience preferred.',
                'salary_min': 90000,
                'salary_max': 130000,
                'location': 'Miami, FL',
                'requirements': ['React Native', 'JavaScript', 'iOS', 'Android'],
                'responsibilities': 'Develop mobile apps, optimize performance, publish to app stores',
                'skills': ['React Native', 'JavaScript', 'iOS', 'Android', 'Redux', 'Firebase'],
                'employment_type': 'full_time',
                'work_mode': 'hybrid',
                'seniority': 'mid',
                'recruiter_email': 'baechuer4@gmail.com'
            },
            {
                'title': 'Cloud Solutions Architect',
                'description': 'Design and implement cloud solutions using AWS. Lead technical architecture decisions.',
                'salary_min': 140000,
                'salary_max': 200000,
                'location': 'Denver, CO',
                'requirements': ['AWS', 'Architecture', 'Python', 'Terraform'],
                'responsibilities': 'Design cloud architecture, lead technical decisions, mentor team',
                'skills': ['AWS', 'Architecture', 'Python', 'Terraform', 'CloudFormation', 'Lambda'],
                'employment_type': 'full_time',
                'work_mode': 'remote',
                'seniority': 'senior',
                'recruiter_email': 'baechuer2@gmail.com'
            },
            {
                'title': 'QA Automation Engineer',
                'description': 'Ensure software quality through automated testing. Experience with test frameworks required.',
                'salary_min': 75000,
                'salary_max': 110000,
                'location': 'Phoenix, AZ',
                'requirements': ['Selenium', 'Python', 'Pytest', 'CI/CD'],
                'responsibilities': 'Write automated tests, maintain test suites, report bugs',
                'skills': ['Selenium', 'Python', 'Pytest', 'Jenkins', 'Docker', 'Git'],
                'employment_type': 'full_time',
                'work_mode': 'onsite',
                'seniority': 'mid',
                'recruiter_email': 'baechuer4@gmail.com'
            }
        ]
        
        # Create jobs
        print("\nCreating jobs...")
        for job_data in jobs_data:
            recruiter = created_users[job_data['recruiter_email']]
            
            # Check if job already exists (only when not clearing)
            if not clear_existing:
                existing_job = Job.query.filter_by(
                    user_id=recruiter.id, 
                    title=job_data['title']
                ).first()
                if existing_job:
                    print(f"Job '{job_data['title']}' already exists for {job_data['recruiter_email']}, skipping...")
                    continue
            
            job = Job(
                user_id=recruiter.id,
                title=job_data['title'],
                description=job_data['description'],
                salary_min=job_data['salary_min'],
                salary_max=job_data['salary_max'],
                location=job_data['location'],
                requirements=job_data['requirements'],
                responsibilities=job_data['responsibilities'],
                skills=job_data['skills'],
                application_deadline=date(2025, 12, 31),  # Future date
                employment_type=job_data['employment_type'],
                work_mode=job_data['work_mode'],
                seniority=job_data['seniority']
            )
            db.session.add(job)
            print(f"Created job: {job_data['title']} at {job_data['location']}")
        
        db.session.commit()
        
        # Create random applications
        print("\nCreating applications...")
        candidates = [
            created_users['baechuer3@gmail.com'],
            created_users['candidate1@gmail.com'],
            created_users['candidate2@gmail.com'],
            created_users['candidate3@gmail.com']
        ]
        all_jobs = Job.query.all()
        
        # Sample application data
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Chris', 'Emma', 'Alex', 'Maria']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        companies = ['Tech Corp', 'Startup Inc', 'Big Corp', 'Innovation Labs', 'Digital Solutions', 'Cloud Systems', 'Data Analytics', 'Mobile First']
        positions = ['Software Engineer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer', 'DevOps Engineer', 'Data Scientist', 'Product Manager', 'UX Designer']
        experiences = ['0-1 years', '1-2 years', '2-3 years', '3-5 years', '5-10 years', '10+ years']
        educations = ['high-school', 'associate', 'bachelor', 'master', 'phd', 'other']
        skills_sets = [
            ['React', 'JavaScript', 'Node.js'],
            ['Python', 'Django', 'PostgreSQL'],
            ['Java', 'Spring Boot', 'MySQL'],
            ['Vue.js', 'TypeScript', 'MongoDB'],
            ['Angular', 'C#', 'SQL Server'],
            ['PHP', 'Laravel', 'Redis'],
            ['Go', 'Docker', 'Kubernetes'],
            ['Ruby', 'Rails', 'Elasticsearch']
        ]
        
        applications_created = 0
        
        # Create 2-4 applications per job randomly
        for job in all_jobs:
            num_applications = random.randint(2, 4)
            # Ensure we don't exceed the number of available candidates
            num_applications = min(num_applications, len(candidates))
            
            # Shuffle candidates to randomize selection
            job_candidates = candidates.copy()
            random.shuffle(job_candidates)
            
            for i in range(num_applications):
                # Select a candidate (each candidate can only apply once per job)
                candidate = job_candidates[i]
                
                # Generate random application data
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                company = random.choice(companies)
                position = random.choice(positions)
                experience = random.choice(experiences)
                education = random.choice(educations)
                skills = random.choice(skills_sets)
                
                # Create a unique email for each application to avoid conflicts
                email = f"{first_name.lower()}.{last_name.lower()}.{job.id}.{i}@example.com"
                
                application = Application(
                    user_id=candidate.id,
                    job_id=job.id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    current_company=company,
                    current_position=position,
                    experience=experience,
                    education=education,
                    skills=', '.join(skills),
                    portfolio=f"https://{first_name.lower()}{last_name.lower()}.dev",
                    linkedin=f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
                    github=f"https://github.com/{first_name.lower()}{last_name.lower()}",
                    availability="Immediate",
                    salary_expectation=str(random.randint(60000, 120000)),
                    notice_period=f"{random.randint(1, 4)} weeks",
                    work_authorization="Yes",
                    relocation=random.choice(["Yes", "No"]),
                    additional_info=f"Passionate {position.lower()} with strong technical skills and {experience} of experience.",
                    status="submitted",
                    resume_path=f"applications/{applications_created + 1}/resume.pdf",
                    cover_letter_path=f"applications/{applications_created + 1}/cover.pdf"
                )
                
                db.session.add(application)
                applications_created += 1
                print(f"Created application: {first_name} {last_name} for {job.title}")
        
        db.session.commit()
        
        # Create actual PDF resume and cover letter files
        print("\nCreating PDF resume and cover letter files...")
        static_folder = Path(current_app.instance_path).parent / 'static'
        applications_folder = static_folder / 'applications'
        applications_folder.mkdir(exist_ok=True)
        
        # Get all applications to create files for them
        all_applications = Application.query.all()
        
        for application in all_applications:
            # Create application-specific folder
            app_folder = applications_folder / str(application.id)
            app_folder.mkdir(exist_ok=True)
            
            # Create PDF resume
            resume_path = app_folder / 'resume.pdf'
            create_pdf_resume(resume_path, application)
            
            # Create PDF cover letter
            cover_path = app_folder / 'cover.pdf'
            create_pdf_cover_letter(cover_path, application)
            
            print(f"Created PDF files for application: {application.first_name} {application.last_name}")
        
        print(f"\n✅ Successfully created:")
        print(f"   - {len(users_data)} users")
        print(f"   - {len(jobs_data)} jobs")
        print(f"   - {applications_created} applications")
        print(f"   - {len(all_applications)} PDF resume and cover letter files")
        print(f"\n👥 User Roles:")
        print(f"   - baechuer1@gmail.com: ADMIN")
        print(f"   - baechuer2@gmail.com: RECRUITER")
        print(f"   - baechuer3@gmail.com: CANDIDATE")
        print(f"   - baechuer4@gmail.com: RECRUITER")
        print(f"   - candidate1@gmail.com: CANDIDATE")
        print(f"   - candidate2@gmail.com: CANDIDATE")
        print(f"   - candidate3@gmail.com: CANDIDATE")
        print(f"\n🔑 Password for all users: 'Password123'")
        print(f"\n💼 Jobs Distribution:")
        baechuer2_jobs = [job for job in jobs_data if job['recruiter_email'] == 'baechuer2@gmail.com']
        baechuer4_jobs = [job for job in jobs_data if job['recruiter_email'] == 'baechuer4@gmail.com']
        print(f"   - baechuer2@gmail.com: {len(baechuer2_jobs)} jobs")
        print(f"   - baechuer4@gmail.com: {len(baechuer4_jobs)} jobs")
        print(f"\n📝 All applications are in 'submitted' status")

def create_pdf_resume(file_path, application):
    """Create a PDF resume for the application"""
    doc = SimpleDocTemplate(str(file_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph(f"TEST RESUME FOR {application.first_name.upper()} {application.last_name.upper()}", title_style))
    story.append(Spacer(1, 12))
    
    # Contact Information
    story.append(Paragraph("<b>Contact Information:</b>", styles['Heading2']))
    story.append(Paragraph(f"Name: {application.first_name} {application.last_name}", styles['Normal']))
    story.append(Paragraph(f"Email: {application.email}", styles['Normal']))
    story.append(Paragraph(f"Phone: {application.phone}", styles['Normal']))
    story.append(Paragraph(f"LinkedIn: {application.linkedin}", styles['Normal']))
    story.append(Paragraph(f"GitHub: {application.github}", styles['Normal']))
    story.append(Paragraph(f"Portfolio: {application.portfolio}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Professional Summary
    story.append(Paragraph("<b>Professional Summary:</b>", styles['Heading2']))
    story.append(Paragraph(f"Experienced {application.current_position} with {application.experience} of experience in {application.skills}. Currently working at {application.current_company}.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Education
    story.append(Paragraph("<b>Education:</b>", styles['Heading2']))
    story.append(Paragraph(application.education.title(), styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Skills
    story.append(Paragraph("<b>Skills:</b>", styles['Heading2']))
    story.append(Paragraph(application.skills, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Additional Information
    story.append(Paragraph("<b>Additional Information:</b>", styles['Heading2']))
    story.append(Paragraph(f"Availability: {application.availability}", styles['Normal']))
    story.append(Paragraph(f"Notice Period: {application.notice_period}", styles['Normal']))
    story.append(Paragraph(f"Work Authorization: {application.work_authorization}", styles['Normal']))
    story.append(Paragraph(f"Relocation: {application.relocation}", styles['Normal']))
    story.append(Paragraph(f"Salary Expectation: ${application.salary_expectation}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(application.additional_info, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph("---", styles['Normal']))
    story.append(Paragraph("This is a test resume file generated by the seed script.", styles['Normal']))
    
    doc.build(story)

def create_pdf_cover_letter(file_path, application):
    """Create a PDF cover letter for the application"""
    doc = SimpleDocTemplate(str(file_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph(f"TEST COVER LETTER FOR {application.first_name.upper()} {application.last_name.upper()}", title_style))
    story.append(Spacer(1, 12))
    
    # Cover letter content
    story.append(Paragraph("Dear Hiring Manager,", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"I am writing to express my strong interest in the {application.job.title} position. As an experienced {application.current_position} with {application.experience} of experience, I am excited about the opportunity to contribute to your team.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"My current role at {application.current_company} has provided me with extensive experience in {application.skills}, which I believe aligns perfectly with the requirements for this position.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Key highlights of my qualifications:</b>", styles['Normal']))
    story.append(Paragraph(f"• {application.experience} of experience in software development", styles['Normal']))
    story.append(Paragraph(f"• Strong background in {application.skills}", styles['Normal']))
    story.append(Paragraph(f"• {application.education.title()} education", styles['Normal']))
    story.append(Paragraph(f"• Available to start {application.availability}", styles['Normal']))
    story.append(Paragraph(f"• Notice period: {application.notice_period}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("I am particularly drawn to this opportunity because of [company's mission/values/specific aspects of the role]. My experience in [relevant skills/technologies] has prepared me to make an immediate impact.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("I am available for an interview at your convenience and look forward to discussing how my skills and experience can contribute to your team's success.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Thank you for considering my application.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Best regards,", styles['Normal']))
    story.append(Paragraph(f"{application.first_name} {application.last_name}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Contact Information
    story.append(Paragraph("<b>Contact Information:</b>", styles['Heading2']))
    story.append(Paragraph(f"Email: {application.email}", styles['Normal']))
    story.append(Paragraph(f"Phone: {application.phone}", styles['Normal']))
    story.append(Paragraph(f"LinkedIn: {application.linkedin}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph("---", styles['Normal']))
    story.append(Paragraph("This is a test cover letter file generated by the seed script.", styles['Normal']))
    
    doc.build(story)

if __name__ == '__main__':
    import sys
    
    # Check if --clear flag is provided
    clear_existing = '--clear' in sys.argv
    
    if clear_existing:
        print("⚠️  WARNING: This will clear all existing data!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            sys.exit(0)
    
    create_users_and_jobs(clear_existing=clear_existing)
