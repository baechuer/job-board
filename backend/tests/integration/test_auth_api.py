def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_register_endpoint_success(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "api@example.com", "password": "Password123!", "username": "apiuser"},
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["email"] == "api@example.com"
    assert "id" in body


def test_register_endpoint_duplicate_email(client):
    client.post(
        "/api/auth/register",
        json={"email": "dupapi@example.com", "password": "Password123!", "username": "u1"},
    )
    res = client.post(
        "/api/auth/register",
        json={"email": "dupapi@example.com", "password": "Password123!", "username": "u2"},
    )
    assert res.status_code in (400, 409, 500)
    body = res.get_json()
    assert "error" in body


def test_login_success_and_me(client):
    client.post(
        "/api/auth/register",
        json={"email": "loginapi@example.com", "password": "Password123!", "username": "loginapi"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "loginapi@example.com", "password": "Password123!"},
    )
    assert res.status_code == 200
    token = res.get_json()["access_token"]

    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.get_json()["user"]["email"] == "loginapi@example.com"


def test_refresh_flow_success(client):
    # Register and login
    client.post(
        "/api/auth/register",
        json={"email": "refresh@example.com", "password": "Password123!", "username": "refreshu"},
    )
    res_login = client.post(
        "/api/auth/login",
        json={"email": "refresh@example.com", "password": "Password123!"},
    )
    assert res_login.status_code == 200
    body = res_login.get_json()
    access = body["access_token"]
    refresh = body["refresh_token"]

    # Call /refresh with refresh token and get a new access token
    res_refresh = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {refresh}"},
    )
    assert res_refresh.status_code == 200
    new_access = res_refresh.get_json()["access_token"]
    assert isinstance(new_access, str) and len(new_access) > 10

    # New access token should work on /me
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert res_me.status_code == 200
    assert res_me.get_json()["user"]["email"] == "refresh@example.com"


def test_logout_all_invalidates_old_tokens_and_refresh(client):
    # Register and login
    client.post(
        "/api/auth/register",
        json={"email": "logoutall@example.com", "password": "Password123!", "username": "logoutallu"},
    )
    res_login = client.post(
        "/api/auth/login",
        json={"email": "logoutall@example.com", "password": "Password123!"},
    )
    assert res_login.status_code == 200
    tokens = res_login.get_json()
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    # Ensure logout timestamp is strictly after token iat (second-level resolution)
    import time
    time.sleep(1)
    # logout_all should set last_logout_at so old tokens are rejected
    res_logout_all = client.post(
        "/api/auth/logout_all",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert res_logout_all.status_code == 200

    # Old access should now fail on /me
    res_me_old = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert res_me_old.status_code == 401

    # Old refresh should also fail to mint a new access token
    res_refresh_old = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {refresh}"},
    )
    assert res_refresh_old.status_code == 401

    # Login again to get fresh tokens
    res_login2 = client.post(
        "/api/auth/login",
        json={"email": "logoutall@example.com", "password": "Password123!"},
    )
    assert res_login2.status_code == 200
    new_access = res_login2.get_json()["access_token"]
    # New access should work
    res_me_new = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert res_me_new.status_code == 200


def test_login_invalid_credentials(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "nouser@example.com", "password": "nope"},
    )
    assert res.status_code == 401
    assert res.get_json()["error"] == "invalid credentials"


