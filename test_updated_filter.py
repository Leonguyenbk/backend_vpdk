#!/usr/bin/env python
"""Test the updated manager filter logic."""
from app.extensions import db
from app.models import User, UserRole, OrgUnit

from app import create_app

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("TEST UPDATED MANAGER FILTER LOGIC")
    print("="*80 + "\n")
    
    # Test with root-level org unit manager (phuonghx in BAN GIÁM ĐỐC)
    director = User.query.filter_by(username="phuonghx").first()
    if director:
        org_unit = OrgUnit.query.get(director.org_unit_id)
        print(f"Director: {director.username} ({director.full_name})")
        print(f"  Org Unit: {org_unit.name} (ID: {org_unit.id}, Parent: {org_unit.parent_id})")
        print(f"  Is BAN GIÁM ĐỐC: {'ban giám đốc' in org_unit.name.lower()}\n")
        
        if org_unit.name and "ban giám đốc" in org_unit.name.lower():
            # See all users
            users = User.query.filter(
                User.id != director.id,
                User.role != UserRole.ADMIN
            ).all()
            print(f"  Filter: ALL users except self & admin (BAN GIÁM ĐỐC user)")
        else:
            # Hierarchical search
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
            
            users = User.query.filter(
                User.org_unit_id.in_(list(unit_ids)),
                User.id != director.id,
                User.role != UserRole.ADMIN
            ).all()
            org_names = [OrgUnit.query.get(uid).name for uid in sorted(unit_ids)]
            print(f"  Filter: Hierarchical search in org units: {org_names}")
        
        print(f"\n  Users visible to director: {len(users)}")
        for u in users:
            org_name = u.org_unit.name if u.org_unit else "NONE"
            print(f"    - {u.username:20} | {u.full_name:20} | Role: {u.role.value:10} | Org: {org_name}")
    
    # Test with non-root manager (user01 in PHÒNG TỐ CHỨC HÀNH CHÍNH)
    print("\n" + "-"*80 + "\n")
    
    manager = User.query.filter_by(username="user01").first()
    if manager:
        org_unit = OrgUnit.query.get(manager.org_unit_id)
        print(f"Manager: {manager.username} ({manager.full_name})")
        print(f"  Org Unit: {org_unit.name} (ID: {org_unit.id}, Parent: {org_unit.parent_id})")
        print(f"  Is BAN GIÁM ĐỐC: {'ban giám đốc' in org_unit.name.lower()}\n")
        
        if org_unit.name and "ban giám đốc" in org_unit.name.lower():
            users = User.query.filter(
                User.id != manager.id,
                User.role != UserRole.ADMIN
            ).all()
            print(f"  Filter: ALL users except self & admin (BAN GIÁM ĐỐC user)")
        else:
            unit_ids = {manager.org_unit_id}
            frontier = {manager.org_unit_id}
            
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
            
            users = User.query.filter(
                User.org_unit_id.in_(list(unit_ids)),
                User.id != manager.id,
                User.role != UserRole.ADMIN
            ).all()
            org_names = [OrgUnit.query.get(uid).name for uid in sorted(unit_ids)]
            print(f"  Filter: Hierarchical search in org units: {org_names}")
        
        print(f"\n  Users visible to manager: {len(users)}")
        for u in users:
            org_name = u.org_unit.name if u.org_unit else "NONE"
            print(f"    - {u.username:20} | {u.full_name:20} | Role: {u.role.value:10} | Org: {org_name}")
    
    print("\n" + "="*80 + "\n")
