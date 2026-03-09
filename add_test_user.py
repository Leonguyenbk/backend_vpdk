#!/usr/bin/env python
"""Add test users to test manager functionality."""
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User, UserRole, OrgUnit, JobTitle

from app import create_app

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("ADDING TEST USERS")
    print("="*60 + "\n")
    
    # Get manager's org unit (user01)
    manager = User.query.filter_by(username="user01").first()
    if not manager:
        print("Manager user01 not found!")
        exit(1)
    
    print(f"Manager: {manager.username} (ID: {manager.id})")
    print(f"  Org Unit: {manager.org_unit.name} (ID: {manager.org_unit_id})\n")
    
    # Get a regular user job title
    user_job_title = JobTitle.query.filter_by(is_manager=False).first()
    if not user_job_title:
        print("No non-manager job title found!")
        exit(1)
    
    print(f"Using job title: {user_job_title.name} (is_manager: {user_job_title.is_manager})\n")
    
    # Create test users in the same org unit as the manager
    test_users = [
        {
            "username": "emp001",
            "full_name": "Nguyễn Văn A",
            "email": "empA@example.com",
            "phone": "0912345601",
            "gender": "Nam",
            "role": UserRole.USER,
        },
        {
            "username": "emp002", 
            "full_name": "Trần Thị B",
            "email": "empB@example.com",
            "phone": "0912345602",
            "gender": "Nữ",
            "role": UserRole.USER,
        },
    ]
    
    for data in test_users:
        # Check if user already exists
        if User.query.filter_by(username=data["username"]).first():
            print(f"✓ {data['username']} already exists, skipping")
            continue
        
        user = User(
            username=data["username"],
            password_hash=generate_password_hash("123456"),
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            gender=data["gender"],
            role=data["role"],
            org_unit_id=manager.org_unit_id,  # Same org unit as manager
            job_title_id=user_job_title.id,
            job_title=user_job_title.name,
        )
        db.session.add(user)
        print(f"✓ Created: {data['username']} ({data['role'].value})")
    
    db.session.commit()
    
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60 + "\n")
    
    org_id = manager.org_unit_id
    users_in_org = User.query.filter_by(org_unit_id=org_id).all()
    
    print(f"Users in {manager.org_unit.name} (org_unit_id={org_id}):\n")
    for u in users_in_org:
        print(f"  - {u.username:15} | {u.full_name:20} | Role: {u.role.value:10}")
    
    # Simulate manager filter
    print(f"\nWhat manager {manager.username} will see (excluding self, admin):\n")
    filtered = User.query.filter(
        User.org_unit_id == org_id,
        User.id != manager.id,
        User.role != UserRole.ADMIN
    ).all()
    
    for u in filtered:
        print(f"  - {u.username:15} | {u.full_name:20} | Role: {u.role.value:10}")
    
    print(f"\nTotal: {len(filtered)} users visible to manager")
    print("\n" + "="*60 + "\n")
