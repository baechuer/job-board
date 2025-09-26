import pytest
from app import create_app
from app.extensions import db


def _mk_client():
    class Cfg:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        JWT_SECRET_KEY = "test"
        SECRET_KEY = "test"
    app = create_app(Cfg)
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    client = app.test_client()
    return app, client, ctx


def _register_user(client, email, username, password="Password123!"):
    client.post('/api/auth/register', json={"email": email, "password": password, "username": username})


def _login(client, email, password="Password123!"):
    return client.post('/api/auth/login', json={"email": email, "password": password}).get_json()


def _add_role(user_id, role):
    from app.models.user_role import UserRole
    from sqlalchemy import select, exists, and_
    # Make idempotent for tests: avoid duplicate insert if role already present
    already_has = db.session.execute(
        select(exists().where(and_(UserRole.user_id == user_id, UserRole.role == role)))
    ).scalar()
    if already_has:
        return
    db.session.add(UserRole(user_id=user_id, role=role))
    db.session.commit()


def test_admin_metrics_and_users():
    app, client, ctx = _mk_client()
    try:
        # Seed users
        _register_user(client, 'admin@example.com', 'admin')
        _register_user(client, 'rec@example.com', 'rec')
        _register_user(client, 'cand@example.com', 'cand')

        # Promote roles
        from app.models.user import User
        admin_id = db.session.query(User).filter_by(email='admin@example.com').first().id
        rec_id = db.session.query(User).filter_by(email='rec@example.com').first().id
        cand_id = db.session.query(User).filter_by(email='cand@example.com').first().id
        _add_role(admin_id, 'admin')
        _add_role(rec_id, 'recruiter')
        _add_role(cand_id, 'candidate')

        # Login as admin
        tokens = _login(client, 'admin@example.com')
        headers = { 'Authorization': f"Bearer {tokens['access_token']}" }

        # Metrics
        m = client.get('/api/admin/metrics', headers=headers)
        assert m.status_code == 200
        body = m.get_json()
        assert 'total_users' in body and body['total_users'] >= 3
        assert 'total_recruiters' in body and body['total_recruiters'] >= 1
        assert 'active_jobs' in body

        # Users - all (no admins)
        u = client.get('/api/admin/users', headers=headers)
        assert u.status_code == 200
        users = u.get_json()['users']
        assert all(row['role'] != 'admin' for row in users)

        # Users - recruiters only
        ur = client.get('/api/admin/users?role=recruiter', headers=headers)
        assert ur.status_code == 200
        recruiters = ur.get_json()['users']
        assert all(row['role'] == 'recruiter' for row in recruiters)

        # Users - candidates only
        uc = client.get('/api/admin/users?role=candidate', headers=headers)
        assert uc.status_code == 200
        candidates = uc.get_json()['users']
        assert all(row['role'] == 'candidate' for row in candidates)

        # Non-admin cannot access
        nt = _login(client, 'rec@example.com')
        nh = { 'Authorization': f"Bearer {nt['access_token']}" }
        forbidden = client.get('/api/admin/users', headers=nh)
        assert forbidden.status_code == 403
    finally:
        db.drop_all()
        ctx.pop()


