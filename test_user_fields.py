import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Add the project root to the Python path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService
from app.core.security import verify_password

def test_phone_number_and_last_login():
    """
    Test that the phone_number field works and last_login is updated on authentication.
    """
    # Create a database session
    db: Session = SessionLocal()
    user_service = UserService(db)
    
    try:
        # 1. Create a test user with phone number
        print("Creating test user...")
        test_user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            phone_number="123-456-7890",
            full_name="Test User",
            bio="This is a test user",
            is_superuser=False
        )
        
        # Try to create the user, but handle the case if it already exists
        try:
            user = user_service.create_user(test_user)
            print(f"User created with ID: {user.id}")
        except Exception as e:
            print(f"User creation failed (might already exist): {str(e)}")
            # Get the user by username if it already exists
            user = user_service.get_user_by_username("testuser")
            if not user:
                print("Could not find or create test user")
                return
        
        # Print initial user data
        print("\nInitial user data:")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Phone number: {getattr(user, 'phone_number', 'Not set')}")
        print(f"Last login: {getattr(user, 'last_login', 'Not set')}")
        
        # 2. Update user with phone number
        print("\nUpdating user with phone number...")
        update_data = UserUpdate(
            phone_number="123-456-7890",
            full_name="Test User Updated",
            bio="Updated test user bio",
            profile_picture=None,
            is_superuser=False
        )
        
        updated_user = user_service.update_user(str(user.id), update_data)
        if updated_user:
            print("User updated successfully")
            print(f"Updated phone number: {getattr(updated_user, 'phone_number', 'Not set')}")
        else:
            print("Failed to update user")
            return
        
        # Store the current last_login value for comparison
        previous_login = getattr(updated_user, 'last_login', None)
        print(f"Previous last_login: {previous_login}")
        
        # 3. Authenticate the user to test last_login update
        print("\nAuthenticating user...")
        authenticated_user = user_service.authenticate_user("testuser", "TestPassword123")
        
        if authenticated_user:
            print("Authentication successful")
            current_login = getattr(authenticated_user, 'last_login', None)
            print(f"New last_login: {current_login}")
            
            # Check if last_login was updated
            if previous_login is None and current_login is not None:
                print("✅ last_login field was successfully set (was previously None)")
            elif previous_login is not None and current_login is not None:
                if current_login > previous_login:
                    print("✅ last_login field was successfully updated")
                else:
                    print("❌ last_login field was not updated")
            else:
                print("❌ last_login field is still None")
            
            # Check if phone_number is present
            phone = getattr(authenticated_user, 'phone_number', None)
            if phone:
                print(f"✅ phone_number field is present: {phone}")
            else:
                print("❌ phone_number field is missing")
        else:
            print("Authentication failed")
    
    finally:
        # Close the database session
        db.close()

if __name__ == "__main__":
    test_phone_number_and_last_login()