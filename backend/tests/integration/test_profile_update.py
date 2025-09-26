import pytest
from app.extensions import db
from sqlalchemy import select
from app.models.user import User
from app.models.verification_code import VerificationCode


def test_request_code_and_verify_and_update_profile(client, make_user, auth_headers):
    user = make_user(is_verified=True)
    headers = auth_headers(user)

    # Request code
    r = client.post('/api/auth/profile/update/request-code', headers=headers)
    assert r.status_code == 200

    # Fetch code from DB (since mail is suppressed in tests)
    vc = db.session.execute(
        select(VerificationCode).where(VerificationCode.user_id == user.id).order_by(VerificationCode.id.desc())
    ).scalar_one()
    assert vc.purpose == 'profile_update'

    # Verify code
    v = client.post('/api/auth/profile/update/verify-code', headers=headers, json={"code": vc.code})
    assert v.status_code == 200

    # Update profile with code
    new_username = user.username + "_x"
    u = client.put('/api/auth/profile', headers=headers, json={
        "username": new_username,
        "code": vc.code,
    })
    assert u.status_code == 200

    # Confirm persisted
    refreshed = db.session.get(User, user.id)
    assert refreshed.username == new_username


def test_update_profile_requires_code(client, make_user, auth_headers):
    user = make_user(is_verified=True)
    headers = auth_headers(user)
    r = client.put('/api/auth/profile', headers=headers, json={"username": "nope"})
    assert r.status_code == 400


def test_verify_code_invalid_or_expired(client, make_user, auth_headers):
    user = make_user(is_verified=True)
    headers = auth_headers(user)
    r = client.post('/api/auth/profile/update/verify-code', headers=headers, json={"code": "000000"})
    assert r.status_code == 400
