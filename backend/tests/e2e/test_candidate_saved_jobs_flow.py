def test_candidate_saved_jobs_e2e(client, auth_headers, make_user, make_job):
    user = make_user(is_verified=True)
    job = make_job(user_id=user.id)

    # Save then unsave through API to simulate end-to-end user actions
    r = client.get(f'/api/candidate/saved-jobs/status/{job.id}', headers=auth_headers(user))
    assert r.status_code == 200 and r.json['saved'] is False

    r = client.post(f'/api/candidate/saved-jobs/{job.id}', headers=auth_headers(user))
    assert r.status_code == 200 and r.json['saved'] is True

    r = client.get('/api/candidate/saved-jobs', headers=auth_headers(user))
    assert r.status_code == 200 and r.json['total'] >= 1

    r = client.delete(f'/api/candidate/saved-jobs/{job.id}', headers=auth_headers(user))
    assert r.status_code == 200 and r.json['saved'] is False


