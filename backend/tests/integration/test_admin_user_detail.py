from app.extensions import db
from app.models.user import User
from app.models.user_role import UserRole
from flask_jwt_extended import create_access_token


def _admin_headers(app, admin_user_id: int):
    token = create_access_token(identity=str(admin_user_id))
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_get_user_detail(app, client):
    # seed admin and normal user
    admin = User(email="admin@example.com", username="admin", password_hash="x")
    admin.roles.append(UserRole(role="admin"))
    user = User(email="user@example.com", username="user", password_hash="y")
    user.roles.append(UserRole(role="candidate"))
    db.session.add_all([admin, user])
    db.session.commit()

    headers = _admin_headers(app, admin.id)
    resp = client.get(f"/api/admin/users/{user.id}", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["email"] == "user@example.com"
    assert body["username"] == "user"


def test_admin_can_update_user_detail(app, client):
    admin = User(email="admin2@example.com", username="admin2", password_hash="x")
    admin.roles.append(UserRole(role="admin"))
    user = User(email="u2@example.com", username="u2", password_hash="y")
    user.roles.append(UserRole(role="candidate"))
    db.session.add_all([admin, user])
    db.session.commit()

    headers = _admin_headers(app, admin.id)
    resp = client.put(
        f"/api/admin/users/{user.id}",
        headers=headers,
        json={"username": "updated", "email": "updated@example.com", "role": "recruiter"},
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body.get("msg") == "user updated"

    refreshed = db.session.get(User, user.id)
    assert refreshed.username == "updated"
    assert refreshed.email == "updated@example.com"

