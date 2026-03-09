#!/usr/bin/env python
"""Check manager account roles."""
from app.extensions import db
from app.models import User, UserRole

from app import create_app

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("CHECK MANAGER ACCOUNT ROLES")
    print("="*80 + "\n")
    
    managers = User.query.filter(
        User.username.in_(["user01", "vuongdn", "phuonghx"])
    ).all()
    
    for m in managers:
        print(f"Username: {m.username}")
        print(f"  Full Name: {m.full_name}")
        print(f"  Role: {m.role} (value: {m.role.value})")
        print(f"  Role type: {type(m.role)}")
        print(f"  Is MANAGER: {m.role == UserRole.MANAGER}")
        print(f"  Is ADMIN: {m.role == UserRole.ADMIN}")
        print()
    
    print("="*80 + "\n")
