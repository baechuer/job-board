def test_full_auth_flow(client):
    # Register
    r1 = client.post(
        "/api/auth/register",
        json={"email": "e2e@example.com", "password": "Password123!", "username": "e2euser"},
    )
    assert r1.status_code == 201

    # Duplicate register should return a clear error
    rdup = client.post(
        "/api/auth/register",
        json={"email": "e2e@example.com", "password": "Password123!", "username": "someoneelse"},
    )
    assert rdup.status_code in (400, 409, 500)
    assert "error" in rdup.get_json()

    # Login
    r2 = client.post(
        "/api/auth/login",
        json={"email": "e2e@example.com", "password": "Password123!"},
    )
    assert r2.status_code == 200
    token = r2.get_json()["access_token"]

    # Me
    r3 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200
    assert r3.get_json()["user"]["email"] == "e2e@example.com"


