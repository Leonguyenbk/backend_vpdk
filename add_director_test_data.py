#!/usr/bin/env python
"""Add test users for director org units."""
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User, UserRole, OrgUnit, JobTitle

from app import create_app

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("ADDING TEST DATA FOR DIRECTOR ORG UNITS")
    print("="*80 + "\n")
    
    # Get job titles
    user_job = JobTitle.query.filter_by(is_manager=False).first()
    
    # Test data for BAN GIÁM ĐỐC (Director office - ID 10)
    ban_giam_doc = OrgUnit.query.get(10)
    if ban_giam_doc:
        print(f"Org Unit: {ban_giam_doc.name} (ID: {ban_giam_doc.id})")
        
        test_users = [
            {
                "username": "admin_staff01",
                "full_name": "Lê Văn C",
                "email": "admin.c@example.com",
                "phone": "0912345701",
                "gender": "Nam",
                "org_unit_id": ban_giam_doc.id,
            },
            {
                "username": "admin_staff02",
                "full_name": "Phạm Thị D",
                "email": "admin.d@example.com",
                "phone": "0912345702",
                "gender": "Nữ",
                "org_unit_id": ban_giam_doc.id,
            },
        ]
        
        for data in test_users:
            if User.query.filter_by(username=data["username"]).first():
                print(f"  ✓ {data['username']} already exists")
                continue
            
            user = User(
                username=data["username"],
                password_hash=generate_password_hash("123456"),
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                gender=data["gender"],
                role=UserRole.USER,
                org_unit_id=data["org_unit_id"],
                job_title_id=user_job.id if user_job else None,
                job_title=user_job.name if user_job else None,
            )
            db.session.add(user)
            print(f"  ✓ Created: {data['username']}")
    
    # Test data for PHÒNG KẾ HOẠCH - TÀI CHÍNH (Finance Dept - ID 8)
    # And its child TỔ KẾ HOẠCH (Planning Team - ID 9)
    finance_dept = OrgUnit.query.get(8)
    if finance_dept:
        print(f"\nOrg Unit: {finance_dept.name} (ID: {finance_dept.id})")
        
        test_users = [
            {
                "username": "finance01",
                "full_name": "Trương Văn E",
                "email": "finance.e@example.com",
                "phone": "0912345703",
                "gender": "Nam",
                "org_unit_id": 9,  # Child unit: TỔ KẾ HOẠCH
            },
            {
                "username": "finance02",
                "full_name": "Ngô Thị F",
                "email": "finance.f@example.com",
                "phone": "0912345704",
                "gender": "Nữ",
                "org_unit_id": 9,
            },
        ]
        
        for data in test_users:
            if User.query.filter_by(username=data["username"]).first():
                print(f"  ✓ {data['username']} already exists")
                continue
            
            user = User(
                username=data["username"],
                password_hash=generate_password_hash("123456"),
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                gender=data["gender"],
                role=UserRole.USER,
                org_unit_id=data["org_unit_id"],
                job_title_id=user_job.id if user_job else None,
                job_title=user_job.name if user_job else None,
            )
            db.session.add(user)
            print(f"  ✓ Created: {data['username']}")
    
    db.session.commit()
    
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80 + "\n")
    
    # Check phuonghx (director)
    director = User.query.filter_by(username="phuonghx").first()
    if director:
        print(f"Director: {director.username} ({director.full_name})")
        print(f"  Org Unit: {director.org_unit.name} (ID: {director.org_unit_id})\n")
        
        # Simulate hierarchical search
        unit_ids = {director.org_unit_id}
        frontier = {director.org_unit_id}
        
        while frontier:
            children = (
                OrgUnit.query.filter(OrgUnit.parent_id.in_(list(frontier)))
                .with_entities(OrgUnit.id)
                .all()
            )
            next_frontier = {c.id for c in children} - unit_ids
            if not next_frontier:
                break
            unit_ids.update(next_frontier)
            frontier = next_frontier
        
        visible_users = User.query.filter(
            User.org_unit_id.in_(list(unit_ids)),
            User.id != director.id,
            User.role != UserRole.ADMIN
        ).all()
        
        print(f"  Org units under director: {[OrgUnit.query.get(uid).name for uid in unit_ids]}")
        print(f"  Users visible to director: {len(visible_users)}")
        for u in visible_users:
            print(f"    - {u.username:20} | {u.full_name}")
    
    print("\n" + "="*80 + "\n")
