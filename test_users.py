#!/usr/bin/env python
"""Test script to check users, their roles, and org units."""
from app.extensions import db
from app.models import User, UserRole, OrgUnit

# Initialize Flask app context
from app import create_app

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("USER ROLES & ORG UNITS CHECK")
    print("="*60 + "\n")
    
    users = User.query.all()
    print(f"Total users: {len(users)}\n")
    
    for u in users:
        org_name = u.org_unit.name if u.org_unit else "NO ORG UNIT"
        job_name = u.job_title_ref.name if u.job_title_ref else (u.job_title or 'None')
        print(f"ID: {u.id} | {u.username:15} | Role: {u.role.value:10} | Org: {org_name:20} | Job: {job_name}")
    
    print("\n" + "="*60)
    print("ROLE BREAKDOWN")
    print("="*60 + "\n")
    
    for role in UserRole:
        count = User.query.filter_by(role=role).count()
        print(f"  {role.value.upper():10} : {count} users")
    
    print("\n" + "="*60)
    print("MANAGER FILTER TEST")
    print("="*60 + "\n")
    
    # Find a manager
    manager = User.query.filter_by(role=UserRole.MANAGER).first()
    if manager:
        print(f"Testing with manager: {manager.username} (ID: {manager.id})")
        print(f"  Manager's org_unit_id: {manager.org_unit_id}")
        print(f"  Manager's org_unit: {manager.org_unit.name if manager.org_unit else 'NONE'}\n")
        
        # Test the query that /manager/users would run
        if manager.org_unit_id:
            # Simplified: just check same org_unit
            users_in_dept = User.query.filter(
                User.org_unit_id == manager.org_unit_id,
                User.id != manager.id,
                User.role == UserRole.USER
            ).all()
            
            print(f"  Users with role=USER in same org_unit: {len(users_in_dept)}")
            for u in users_in_dept:
                print(f"    - {u.username} ({u.full_name})")
            
            # Also check what we would get without the role filter
            users_all = User.query.filter(
                User.org_unit_id == manager.org_unit_id,
                User.id != manager.id,
            ).all()
            print(f"\n  All users (excluding manager) in same org_unit: {len(users_all)}")
            for u in users_all:
                print(f"    - {u.username:15} | Role: {u.role.value:10}")
        else:
            print("  Manager not assigned to any org_unit!")
    else:
        print("No manager found in database!")
    
    print("\n" + "="*60 + "\n")
