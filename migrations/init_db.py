#!/usr/bin/env python3
"""Database initialization script

This script creates the initial database tables and optionally
creates a default admin user and sample OAuth application.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.models import User, Role, Employee, Branch, Department, Position, user_roles
from app.services.user_service import UserService
from app.schemas.user import UserCreate

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    engine = create_engine(settings.database_url)
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE;"))
        connection.execute(text("CREATE SCHEMA public;"))

    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")
    return engine

def create_admin_user(db_session):
    """Create a default admin user"""
    print("Creating admin user...")
    
    user_service = UserService(db_session)
    
    # Check if admin user already exists
    existing_user = user_service.get_user_by_email("admin@example.com")
    if existing_user:
        print("✓ Admin user already exists")
        return existing_user
    
    # Create admin user
    admin_data = UserCreate(
        username="admin",
        email="admin@example.com",
        password="Admin123!"
    )
    
    admin_user = user_service.create_user(admin_data)
    
    # Activate and verify the user
    user_service.activate_user(admin_user.id)
    user_service.verify_user(admin_user.id)
    
    print("✓ Admin user created successfully")

    print(f"  Username: admin")
    print(f"  Email: admin@example.com")
    print(f"  Password: Admin123!")
    print(f"  User ID: {admin_user.id}")
    
    return admin_user



def main():
    """Main initialization function"""
    print("=" * 50)
    print("FastAPI SSO Database Initialization")
    print("=" * 50)
    
    try:
        # Create database tables
        engine = create_tables()
        
        # Create database session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Create admin user
            admin_user = create_admin_user(db)

            # Commit all changes
            db.commit()
            
            print("\n" + "=" * 50)
            print("✓ Database initialization completed successfully!")
            print("=" * 50)
            print("\nNext steps:")
            print("1. Start the application: uvicorn app.main:app --reload")
            print("2. Visit http://localhost:8000/docs for API documentation")
            print("3. Login with admin credentials to test the system")

            print("\nImportant: Change the admin password in production!")
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()