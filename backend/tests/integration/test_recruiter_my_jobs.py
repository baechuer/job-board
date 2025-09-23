def auth_header(token):
  return {"Authorization": f"Bearer {token}"}


def test_my_jobs_returns_jobs(client):
  # Register and login
  email = "myjobs@example.com"
  client.post("/api/auth/register", json={"email": email, "password": "Password123!", "username": "mj"})
  access = client.post("/api/auth/login", json={"email": email, "password": "Password123!"}).get_json()["access_token"]

  # Create two jobs
  payload = {
    "title": "Role1",
    "description": "Description long enough",
    "salary_min": 1,
    "salary_max": 2,
    "location": "Remote",
    "requirements": ["req"],
    "responsibilities": "resp",
    "skills": ["skill"],
    "application_deadline": "2025-10-31",
  }
  client.post("/api/recruiter/create-job", json=payload, headers=auth_header(access))
  payload["title"] = "Role2"
  client.post("/api/recruiter/create-job", json=payload, headers=auth_header(access))

  # Get my jobs
  res = client.get("/api/recruiter/my-jobs", headers=auth_header(access))
  assert res.status_code == 200
  data = res.get_json()
  assert "jobs" in data
  assert len(data["jobs"]) == 2
  assert data["jobs"][0]["title"] == "Role2"
  assert data["jobs"][0]["status"] in ["active","deprecated"]


def test_my_job_detail(client):
  email = "myjobdetail@example.com"
  client.post("/api/auth/register", json={"email": email, "password": "Password123!", "username": "mjd"})
  access = client.post("/api/auth/login", json={"email": email, "password": "Password123!"}).get_json()["access_token"]
  payload = {
    "title": "Detail",
    "description": "Detail desc long",
    "salary_min": 1,
    "salary_max": 2,
    "location": "Remote",
    "requirements": ["req"],
    "responsibilities": "resp",
    "skills": ["skill"],
    "application_deadline": "2030-10-31",
  }
  res_create = client.post("/api/recruiter/create-job", json=payload, headers=auth_header(access))
  assert res_create.status_code == 201
  job_id = res_create.get_json()["job"]["id"]

  res = client.get(f"/api/recruiter/my-jobs/{job_id}", headers=auth_header(access))
  assert res.status_code == 200
  job = res.get_json()
  assert job["id"] == job_id
  assert job["title"] == "Detail"


def test_my_jobs_status_filter_and_pagination(client):
  email = "filterpage@example.com"
  client.post("/api/auth/register", json={"email": email, "password": "Password123!", "username": "fp"})
  access = client.post("/api/auth/login", json={"email": email, "password": "Password123!"}).get_json()["access_token"]

  # Create active and deprecated
  active_payload = {
    "title": "Active1",
    "description": "desc long enough",
    "salary_min": 1,
    "salary_max": 2,
    "location": "Remote",
    "requirements": ["req"],
    "responsibilities": "resp",
    "skills": ["skill"],
    "application_deadline": "2030-10-31",
  }
  dep_payload = dict(active_payload, title="Old1", application_deadline="2020-01-01")
  client.post("/api/recruiter/create-job", json=active_payload, headers=auth_header(access))
  client.post("/api/recruiter/create-job", json=dep_payload, headers=auth_header(access))

  # Active filter returns only active
  res_active = client.get("/api/recruiter/my-jobs?status=active", headers=auth_header(access))
  assert res_active.status_code == 200
  data_active = res_active.get_json()
  assert all(j.get("status") == "active" for j in data_active["jobs"]) or len(data_active["jobs"]) == 0

  # Deprecated filter returns only deprecated
  res_dep = client.get("/api/recruiter/my-jobs?status=deprecated", headers=auth_header(access))
  assert res_dep.status_code == 200
  data_dep = res_dep.get_json()
  assert all(j.get("status") == "deprecated" for j in data_dep["jobs"]) or len(data_dep["jobs"]) == 0

  # Pagination: per_page=1 returns one item and pages >=1
  res_page = client.get("/api/recruiter/my-jobs?status=active&per_page=1&page=1", headers=auth_header(access))
  data_page = res_page.get_json()
  assert len(data_page["jobs"]) <= 1
  assert data_page["current_page"] == 1


def test_update_about_team_persists_and_shows_in_detail(client):
  email = "editabout@example.com"
  client.post("/api/auth/register", json={"email": email, "password": "Password123!", "username": "abt"})
  access = client.post("/api/auth/login", json={"email": email, "password": "Password123!"}).get_json()["access_token"]
  payload = {
    "title": "AboutTeam",
    "description": "desc long enough",
    "salary_min": 1,
    "salary_max": 2,
    "location": "Remote",
    "requirements": ["req"],
    "responsibilities": "resp",
    "skills": ["skill"],
    "application_deadline": "2030-10-31",
  }
  res_create = client.post("/api/recruiter/create-job", json=payload, headers=auth_header(access))
  job_id = res_create.get_json()["job"]["id"]

  # Update about_team
  res_update = client.put(f"/api/recruiter/my-jobs/{job_id}", json={"about_team": "We are a small, agile team."}, headers=auth_header(access))
  assert res_update.status_code == 200
  assert res_update.get_json().get("about_team") == "We are a small, agile team."

  # Fetch detail and verify
  res_detail = client.get(f"/api/recruiter/my-jobs/{job_id}", headers=auth_header(access))
  assert res_detail.status_code == 200
  assert res_detail.get_json().get("about_team") == "We are a small, agile team."


def test_metrics_counts_active_jobs(client):
  email = "metrics@example.com"
  client.post("/api/auth/register", json={"email": email, "password": "Password123!", "username": "m"})
  access = client.post("/api/auth/login", json={"email": email, "password": "Password123!"}).get_json()["access_token"]
  base = {
    "description": "desc long enough",
    "salary_min": 1,
    "salary_max": 2,
    "location": "Remote",
    "requirements": ["req"],
    "responsibilities": "resp",
    "skills": ["skill"],
    "application_deadline": "2030-10-31",
  }
  # Create two active jobs
  client.post("/api/recruiter/create-job", json={"title": "J1", **base}, headers=auth_header(access))
  client.post("/api/recruiter/create-job", json={"title": "J2", **base}, headers=auth_header(access))

  # Sanity: list active should see 2
  res_list = client.get("/api/recruiter/my-jobs?status=active", headers=auth_header(access))
  assert res_list.status_code == 200
  assert len(res_list.get_json()["jobs"]) == 2

  res = client.get("/api/recruiter/metrics", headers=auth_header(access))
  assert res.status_code == 200
  data = res.get_json()
  assert data["active_jobs"] == 2

