"""Integration tests for user roles behavior."""

from sqlalchemy import select, func
from app.extensions import db
from app.models.user import User
from app.models.user_role import UserRole


def test_register_assigns_candidate_role_by_default(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "roledefault@example.com", "password": "Password123!", "username": "roledefault"},
    )
    assert res.status_code == 201
    user_id = res.get_json()["id"]

    user = db.session.execute(select(User).where(User.id == int(user_id))).scalar_one()
    roles = [r.role for r in user.roles]
    assert "candidate" in roles


def test_role_unique_per_user(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "roleunique@example.com", "password": "Password123!", "username": "roleunique"},
    )
    assert res.status_code == 201
    user_id = int(res.get_json()["id"])

    # Attempt to add duplicate candidate role should violate unique constraint
    user = db.session.get(User, user_id)
    user.roles.append(UserRole(role="candidate"))
    try:
        db.session.commit()
        committed = True
    except Exception:
        db.session.rollback()
        committed = False

    assert committed is False


def test_cascade_delete_user_deletes_roles(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "cascade@example.com", "password": "Password123!", "username": "cascadeuser"},
    )
    assert res.status_code == 201
    user_id = int(res.get_json()["id"])

    # Ensure one role exists
    count_roles_before = db.session.execute(
        select(func.count()).select_from(UserRole).where(UserRole.user_id == user_id)
    ).scalar()
    assert count_roles_before >= 1

    # Delete user
    user = db.session.get(User, user_id)
    db.session.delete(user)
    db.session.commit()

    # Roles should be deleted due to cascade
    count_roles_after = db.session.execute(
        select(func.count()).select_from(UserRole).where(UserRole.user_id == user_id)
    ).scalar()
    assert count_roles_after == 0


