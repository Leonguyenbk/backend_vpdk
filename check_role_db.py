#!/usr/bin/env python
"""Check role values in database."""
import sqlalchemy
from app.extensions import db
from app.models import User, UserRole

from app import create_app

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("CHECK ROLE VALUES IN DATABASE")
    print("="*80 + "\n")
    
    # Query raw SQL to see what's in the DB
    result = db.session.execute(
        sqlalchemy.text("SELECT id, username, role FROM user WHERE username IN ('user01', 'vuongdn', 'phuonghx', 'admin')")
    )
    
    print("Raw database values:")
    for row in result:
        print(f"  ID: {row[0]}, Username: {row[1]:15}, Role (raw): '{row[2]}'")
    
    print("\n" + "="*80)
    print("VERIFY ROLE ENUM COMPARISON")
    print("="*80 + "\n")
    
    # Check how UserRole enum is defined
    print(f"UserRole enum members:")
    for role in UserRole:
        print(f"  {role.name:10} (name) -> {role.value:10} (value)")
    
    # Test comparison
    manager = User.query.filter_by(username="user01").first()
    print(f"\nTest with user01:")
    print(f"  m.role: {manager.role}")
    print(f"  m.role.name: {manager.role.name}")
    print(f"  m.role.value: {manager.role.value}")
    print(f"  m.role == UserRole.MANAGER: {manager.role == UserRole.MANAGER}")
    print(f"  m.role.value == 'manager': {manager.role.value == 'manager'}")
    
    print("\n" + "="*80 + "\n")
