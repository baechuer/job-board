from app.services.saved_job_service import SavedJobService


def test_save_and_unsave_flow(app, make_user, make_job):
    with app.app_context():
        svc = SavedJobService()
        user = make_user(is_verified=True)
        job = make_job(user_id=user.id)

        assert svc.is_saved(user.id, job.id) is False
        svc.save(user.id, job.id)
        assert svc.is_saved(user.id, job.id) is True
        svc.unsave(user.id, job.id)
        assert svc.is_saved(user.id, job.id) is False


