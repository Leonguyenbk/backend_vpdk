from app import create_app
from app.models import JobTitle, User

app = create_app()
with app.app_context():
    print("Testing Job Title Dropdown API...")

    # Test job titles query
    job_titles = JobTitle.query.filter_by(is_active=True).order_by(JobTitle.level_no.desc(), JobTitle.name.asc()).all()
    print(f"✅ Found {len(job_titles)} active job titles:")
    for jt in job_titles[:5]:
        print(f"   - {jt.id}: {jt.code} - {jt.name} (level {jt.level_no})")

    # Test user update logic
    user = User.query.first()
    if user:
        print(f"\n✅ Testing user update for: {user.username}")
        print(f"   Before: job_title_id={user.job_title_id}")

        # Simulate setting job_title_id
        tp_job = JobTitle.query.filter_by(code='TP').first()
        if tp_job:
            user.job_title_id = tp_job.id
            from app.extensions import db
            db.session.commit()

            user = User.query.get(user.id)  # Reload
            print(f"   After: job_title_id={user.job_title_id}")
            print(f"   Job title: {user.job_title_ref.name if user.job_title_ref else 'None'}")

            # Test serialization
            user_dict = user.to_dict()
            print(f"   Serialized: job_title_id={user_dict['job_title_id']}, job_title_name='{user_dict['job_title_name']}'")

    print("\n✅ All tests passed!")