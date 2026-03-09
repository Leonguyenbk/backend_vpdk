#!/usr/bin/env python
"""Check director accounts and their departments."""
from app.extensions import db
from app.models import User, UserRole, OrgUnit, JobTitle

from app import create_app

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("DIRECTOR ACCOUNTS & ORG UNIT CHECK")
    print("="*80 + "\n")
    
    # Find all managers (directors, deputies, etc.)
    managers = User.query.filter_by(role=UserRole.MANAGER).all()
    
    print(f"Total Managers: {len(managers)}\n")
    
    for mgr in managers:
        org_name = mgr.org_unit.name if mgr.org_unit else "NO ORG UNIT"
        job_name = mgr.job_title_ref.name if mgr.job_title_ref else mgr.job_title
        print(f"Manager ID {mgr.id}: {mgr.username:15} | Name: {mgr.full_name:20}")
        print(f"  Job Title: {job_name}")
        print(f"  Org Unit ID: {mgr.org_unit_id} | Name: {org_name}")
        
        if mgr.org_unit_id:
            # Check users in the same org unit
            users_same_org = User.query.filter(
                User.org_unit_id == mgr.org_unit_id,
                User.id != mgr.id,
                User.role != UserRole.ADMIN
            ).all()
            
            print(f"  Users visible to this manager: {len(users_same_org)}")
            for u in users_same_org:
                print(f"    - {u.username:15} | {u.full_name:20} | Role: {u.role.value}")
        
        # Also check if org unit has children (departments)
        if mgr.org_unit:
            children = OrgUnit.query.filter_by(parent_id=mgr.org_unit_id).all()
            if children:
                print(f"  Org unit has {len(children)} child units:")
                for child in children:
                    print(f"    - {child.name} (ID: {child.id})")
                    # Users in child units
                    users_child = User.query.filter(
                        User.org_unit_id == child.id,
                        User.role != UserRole.ADMIN
                    ).all()
                    print(f"      Users in this child: {len(users_child)}")
                    for u in users_child:
                        print(f"        - {u.username} ({u.role.value})")
        
        print()
    
    print("="*80)
    print("ALL ORG UNITS & USER COUNT")
    print("="*80 + "\n")
    
    all_orgs = OrgUnit.query.all()
    for org in all_orgs:
        user_count = User.query.filter_by(org_unit_id=org.id).count()
        parent_name = "ROOT" if org.parent_id is None else f"ID:{org.parent_id}"
        print(f"  {org.id:3} | {org.name:30} | Parent: {parent_name:10} | Users: {user_count}")
    
    print("\n" + "="*80 + "\n")
