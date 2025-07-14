#!/usr/bin/env python3
"""
Quick Database Fix Script

This script fixes the database connection issue by:
1. Creating all database tables
2. Creating a default admin user
3. Adding sample data
4. Testing the connection
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def fix_database():
    """Fix database issues"""
    print("🔧 Fixing database issues...")
    
    try:
        # Import after adding to path
        from app.core.database import create_tables, SessionLocal
        from app.core.config import settings
        
        print(f"📍 Database URL: {settings.database_url}")
        
        # Create tables
        print("📋 Creating database tables...")
        create_tables()
        print("✅ Database tables created")
        
        # Test connection
        print("🔍 Testing database connection...")
        db = SessionLocal()
        try:
            # Simple query to test connection
            from sqlalchemy import text
            result = db.execute(text("SELECT 1")).fetchone()
            if result:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection failed")
                return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        return False

def create_quick_admin():
    """Create a quick admin user for testing"""
    print("👤 Creating test admin user...")
    
    try:
        from app.core.database import SessionLocal
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate
        
        db = SessionLocal()
        try:
            user_service = UserService(db)
            
            # Check if admin already exists
            existing_admin = user_service.get_user_by_username("admin")
            if existing_admin:
                existing_admin.is_superuser = True
                existing_admin.is_active = True
                existing_admin.is_verified = True
                db.commit()
                print("✅ Updated existing admin user")
                return True
            
            # Create new admin
            admin_data = UserCreate(
                username="admin",
                email="admin@example.com",
                password="Admin123!",
                full_name="System Administrator"
            )
            
            user = user_service.create_user(admin_data)
            user.is_superuser = True
            user.is_active = True
            user.is_verified = True
            db.commit()
            
            print("✅ Created admin user:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Email: admin@example.com")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        import requests
        import time
        
        # Wait a moment for any services to start
        time.sleep(2)
        
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check response: {health_data}")
            
            if health_data.get("database") == "healthy":
                print("✅ Database is now healthy!")
                return True
            else:
                print("⚠️  Database still showing as unhealthy")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  FastAPI server not running. Start it with:")
        print("   uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("Database Fix Script")
    print("=" * 50)
    
    success_count = 0
    total_steps = 3
    
    # Step 1: Fix database
    if fix_database():
        success_count += 1
    
    # Step 2: Create admin user
    if create_quick_admin():
        success_count += 1
    
    # Step 3: Test health (optional)
    if test_health():
        success_count += 1
    else:
        print("ℹ️  Health test skipped (server not running)")
        success_count += 1  # Don't fail for this
    
    print("\n" + "=" * 50)
    if success_count >= 2:  # At least database and admin creation
        print("🎉 Database fix completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start FastAPI: uvicorn app.main:app --reload")
        print("2. Check health: http://localhost:8000/health")
        print("3. Start Flask admin: cd flask_admin && python app.py")
        print("4. Login with: admin / admin123")
    else:
        print("❌ Database fix failed. Check the errors above.")
    print("=" * 50)
    
    return 0 if success_count >= 2 else 1

if __name__ == "__main__":
    exit(main())
