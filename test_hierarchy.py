#!/usr/bin/env python
"""Test the hierarchical org unit search."""
from app.extensions import db
from app.models import User, UserRole, OrgUnit

from app import create_app

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("TEST HIERARCHICAL ORG UNIT SEARCH")
    print("="*80 + "\n")
    
    # Test with manager user01
    manager = User.query.filter_by(username="user01").first()
    if not manager:
        print("Manager not found!")
        exit(1)
    
    print(f"Testing with manager: {manager.username}")
    print(f"  Manager org_unit_id: {manager.org_unit_id}")
    print(f"  Manager org_unit: {manager.org_unit.name}\n")
    
    # Replicate the backend query logic
    unit_ids = {manager.org_unit_id}
    frontier = {manager.org_unit_id}
    
    iteration = 0
    while frontier:
        iteration += 1
        print(f"Iteration {iteration}:")
        print(f"  Current frontier: {frontier}")
        print(f"  Total unit_ids collected: {unit_ids}")
        
        children = (
            OrgUnit.query.filter(OrgUnit.parent_id.in_(list(frontier)))
            .with_entities(OrgUnit.id)
            .all()
        )
        
        child_ids = {c.id for c in children}
        print(f"  Found {len(children)} child org units: {child_ids}")
        
        next_frontier = child_ids - unit_ids
        print(f"  Next frontier: {next_frontier}")
        
        if not next_frontier:
            print("  → No more children, stopping")
            break
        
        unit_ids.update(next_frontier)
        frontier = next_frontier
        iteration += 1
        if iteration > 10:
            print("  → Too many iterations, breaking")
            break
    
    print(f"\nFinal unit_ids: {unit_ids}")
    print(f"Which represent: {[OrgUnit.query.get(uid).name for uid in unit_ids]}\n")
    
    # Now test the user query with these unit_ids
    users = User.query.filter(
        User.org_unit_id.in_(list(unit_ids)),
        User.id != manager.id,
        User.role != UserRole.ADMIN
    ).all()
    
    print(f"Users found with this filter: {len(users)}")
    for u in users:
        print(f"  - {u.username:15} | Org: {u.org_unit.name if u.org_unit else 'NONE':30}")
    
    print("\n" + "="*80 + "\n")
