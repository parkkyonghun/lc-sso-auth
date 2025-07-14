#!/usr/bin/env python3
"""
Script to create a test admin user with a known password
"""

import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def create_test_admin():
    """Create a test admin user"""
    db: Session = SessionLocal()

    try:
        # Create a new admin user with a known password
        hashed_password = hash_password("admin123")
        admin_user = User(
            username="testadmin",
            email="testadmin@example.com",
            hashed_password=hashed_password,
            full_name="Test Administrator",
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()

        print("✅ Test admin user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Is Superuser: {admin_user.is_superuser}")
        print(f"   Is Active: {admin_user.is_active}")
        print(f"   Is Verified: {admin_user.is_verified}")
        print("\n🔑 You can now login with:")
        print("   Username: testadmin")
        print("   Password: admin123")

        return True

    except Exception as e:
        print(f"❌ Error creating test admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Creating test admin user...")
    success = create_test_admin()

    if not success:
        sys.exit(1)