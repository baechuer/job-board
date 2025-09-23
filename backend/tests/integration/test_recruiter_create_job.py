import pytest
from flask import url_for
from app.extensions import db
from app.models.job import Job
from sqlalchemy import select


def auth_header(access_token):
    return {"Authorization": f"Bearer {access_token}"}


def test_create_job_201(client, app, db):
    # Create and login a user
    register = client.post("/api/auth/register", json={"email":"rec@example.com","password":"Password123!","username":"rec"})
    assert register.status_code == 201
    login = client.post("/api/auth/login", json={"email":"rec@example.com","password":"Password123!"})
    access = login.get_json()["access_token"]
    payload = {
        "title": "Data Engineer",
        "description": "ETL pipelines",
        "salary_min": 90000,
        "salary_max": 130000,
        "location": "NYC",
        "requirements": ["Python"],
        "responsibilities": "Maintain pipelines",
        "skills": ["Airflow"],
        "application_deadline": "2025-10-31",
    }
    res = client.post("/api/recruiter/create-job", json=payload, headers=auth_header(access))
    assert res.status_code == 201, res.json
    assert res.json["status"] == "created"

    job = db.session.execute(select(Job).where(Job.title == "Data Engineer")).scalar_one()
    assert job.location == "NYC"


def test_create_job_400_validation(client, app, db):
    client.post("/api/auth/register", json={"email":"rec2@example.com","password":"Password123!","username":"rec2"})
    access = client.post("/api/auth/login", json={"email":"rec2@example.com","password":"Password123!"}).get_json()["access_token"]
    bad = {"title": "x"}  # missing required fields
    res = client.post("/api/recruiter/create-job", json=bad, headers=auth_header(access))
    assert res.status_code == 400
    assert "details" in res.json


def test_create_job_409_conflict(client, app, db):
    client.post("/api/auth/register", json={"email":"rec3@example.com","password":"Password123!","username":"rec3"})
    access = client.post("/api/auth/login", json={"email":"rec3@example.com","password":"Password123!"}).get_json()["access_token"]
    payload = {
        "title": "Platform Engineer",
        "description": "Infra work",
        "salary_min": 100000,
        "salary_max": 140000,
        "location": "Remote",
        "requirements": ["Kubernetes"],
        "responsibilities": "Operate clusters",
        "skills": ["K8s"],
        "application_deadline": "2025-10-31",
    }
    res1 = client.post("/api/recruiter/create-job", json=payload, headers=auth_header(access))
    assert res1.status_code == 201
    res2 = client.post("/api/recruiter/create-job", json=payload, headers=auth_header(access))
    assert res2.status_code == 409
    assert "error" in res2.json


