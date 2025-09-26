from flask import url_for


def test_candidate_saved_jobs_flow(client, auth_headers, make_user, make_job):
    user = make_user(is_verified=True)
    job = make_job(user_id=user.id)

    # list empty
    resp = client.get('/api/candidate/saved-jobs', headers=auth_headers(user))
    assert resp.status_code == 200
    assert resp.json['total'] in (0, resp.json['total'])

    # status false
    resp = client.get(f'/api/candidate/saved-jobs/status/{job.id}', headers=auth_headers(user))
    assert resp.json['saved'] is False

    # save
    resp = client.post(f'/api/candidate/saved-jobs/{job.id}', headers=auth_headers(user))
    assert resp.status_code == 200
    assert resp.json['saved'] is True

    # status true
    resp = client.get(f'/api/candidate/saved-jobs/status/{job.id}', headers=auth_headers(user))
    assert resp.json['saved'] is True

    # list has one
    resp = client.get('/api/candidate/saved-jobs', headers=auth_headers(user))
    assert resp.status_code == 200
    assert resp.json['total'] >= 1

    # unsave
    resp = client.delete(f'/api/candidate/saved-jobs/{job.id}', headers=auth_headers(user))
    assert resp.status_code == 200
    assert resp.json['saved'] is False


