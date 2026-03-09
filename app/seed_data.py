"""
Seed initial job titles into the database.
Run after migration: python -c "from app.seed_data import seed_job_titles; seed_job_titles()"
"""

from app.extensions import db
from app.models import JobTitle


def seed_job_titles():
    """
    Seed initial Vietnamese job titles with appropriate scopes.
    Safe to run multiple times (idempotent).
    """
    
    job_titles_data = [
        # Director level (all access)
        {
            "code": "GD_VP",
            "name": "Giám đốc Văn phòng",
            "level_no": 5,
            "is_manager": True,
            "data_scope": "all",
        },
        {
            "code": "PGD_VP",
            "name": "Phó Giám đốc Văn phòng",
            "level_no": 4,
            "is_manager": True,
            "data_scope": "all",
        },
        # Branch level (subtree access)
        {
            "code": "GD_CN",
            "name": "Giám đốc Chi nhánh",
            "level_no": 4,
            "is_manager": True,
            "data_scope": "subtree",
        },
        {
            "code": "PGD_CN",
            "name": "Phó Giám đốc Chi nhánh",
            "level_no": 3,
            "is_manager": True,
            "data_scope": "subtree",
        },
        # Department level (subtree access)
        {
            "code": "TP",
            "name": "Trưởng phòng",
            "level_no": 4,
            "is_manager": True,
            "data_scope": "subtree",
        },
        {
            "code": "PTP",
            "name": "Phó Trưởng phòng",
            "level_no": 3,
            "is_manager": True,
            "data_scope": "subtree",
        },
        # Team/Unit level (unit access)
        {
            "code": "TO_TRUONG",
            "name": "Tổ trưởng",
            "level_no": 2,
            "is_manager": True,
            "data_scope": "unit",
        },
        {
            "code": "TBP_CN",
            "name": "Trưởng bộ phận chi nhánh",
            "level_no": 2,
            "is_manager": True,
            "data_scope": "unit",
        },
        {
            "code": "PTBP_CN",
            "name": "Phó trưởng bộ phận",
            "level_no": 2,
            "is_manager": True,
            "data_scope": "unit",
        },
        # Staff level (self only)
        {
            "code": "NV",
            "name": "Nhân viên",
            "level_no": 1,
            "is_manager": False,
            "data_scope": "self",
        },
    ]
    
    # Check if already seeded
    existing_count = JobTitle.query.count()
    if existing_count > 0:
        print(f"✓ Job titles already seeded ({existing_count} found). Skipping seed.")
        return
    
    print("Seeding job titles...")
    for data in job_titles_data:
        job_title = JobTitle(**data, is_active=True)
        db.session.add(job_title)
        print(f"  ✓ Added: {data['code']} - {data['name']} (scope: {data['data_scope']})")
    
    db.session.commit()
    print(f"✓ Successfully seeded {len(job_titles_data)} job titles")


if __name__ == "__main__":
    seed_job_titles()
