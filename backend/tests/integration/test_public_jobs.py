def auth_header(access_token):
  return {"Authorization": f"Bearer {access_token}"}


def _base_job_payload():
  return {
    "description": "This is a sufficiently long description.",
    "salary_min": 10,
    "salary_max": 20,
    "location": "Remote",
    "requirements": ["req1"],
    "responsibilities": "Do things",
    "skills": ["python", "react"],
    "application_deadline": "2030-12-31",
  }


def test_public_jobs_lists_active_and_supports_search(client):
  # Create user and some jobs
  email = "browse@example.com"
  client.post("/api/auth/register", json={"email": email, "password": "Password123!", "username": "browse"})
  access = client.post("/api/auth/login", json={"email": email, "password": "Password123!"}).get_json()["access_token"]

  base = _base_job_payload()
  client.post("/api/recruiter/create-job", json={"title": "Senior Python Engineer", **base}, headers=auth_header(access))
  client.post("/api/recruiter/create-job", json={"title": "Frontend React Developer", **base}, headers=auth_header(access))

  # Public list without query
  res = client.get("/api/recruiter/jobs")
  assert res.status_code == 200
  data = res.get_json()
  assert data["total"] >= 2
  titles = [j["title"] for j in data["jobs"]]
  assert any("Python" in t for t in titles)

  # Search by title
  res_q = client.get("/api/recruiter/jobs?q=React")
  assert res_q.status_code == 200
  data_q = res_q.get_json()
  assert any("React" in j["title"] for j in data_q["jobs"]) 
  assert all(("React" in j["title"]) or ("react" in ",".join(j.get("skills", []))) for j in data_q["jobs"]) 

  # Search by skill
  res_skill = client.get("/api/recruiter/jobs?q=python")
  assert res_skill.status_code == 200
  data_skill = res_skill.get_json()
  assert len(data_skill["jobs"]) >= 1


def test_public_job_detail_returns_job_for_active(client):
  email = "detailok@example.com"
  client.post("/api/auth/register", json={"email": email, "password": "Password123!", "username": "d1"})
  access = client.post("/api/auth/login", json={"email": email, "password": "Password123!"}).get_json()["access_token"]
  payload = {"title": "Public Detail", **_base_job_payload()}
  res_create = client.post("/api/recruiter/create-job", json=payload, headers=auth_header(access))
  assert res_create.status_code == 201
  job_id = res_create.get_json()["job"]["id"]

  res = client.get(f"/api/recruiter/jobs/{job_id}")
  assert res.status_code == 200
  assert res.get_json().get("title") == "Public Detail"


def test_public_job_detail_404_for_deprecated(client):
  email = "detail404@example.com"
  client.post("/api/auth/register", json={"email": email, "password": "Password123!", "username": "d2"})
  access = client.post("/api/auth/login", json={"email": email, "password": "Password123!"}).get_json()["access_token"]
  payload = _base_job_payload()
  payload["application_deadline"] = "2020-01-01"  # Past date -> deprecated
  res_create = client.post("/api/recruiter/create-job", json={"title": "Old Job", **payload}, headers=auth_header(access))
  assert res_create.status_code == 201
  job_id = res_create.get_json()["job"]["id"]

  res = client.get(f"/api/recruiter/jobs/{job_id}")
  assert res.status_code == 404

