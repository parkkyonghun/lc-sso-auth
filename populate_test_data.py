import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime
from uuid import UUID

# Add the project root to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from core.database import SessionLocal, engine, Base
from core.config import settings
from app.models.user import User
from app.models.branch import Branch
from app.models.department import Department
from app.models.position import Position

def populate_test_data(db: Session):
    print("Populating test data for branches, departments, and positions...")

    def ensure_entity(session, model, identifier_field, identifier_value, defaults=None, id_value=None):
        query_filter = {identifier_field: identifier_value}
        instance = session.query(model).filter_by(**query_filter).first()
        if instance:
            # Update existing instance
            for key, value in (defaults or {}).items():
                setattr(instance, key, value)
            if id_value and str(instance.id) != str(id_value):
                print(f"Warning: Entity {model.__name__} with {identifier_field}={identifier_value} found but ID mismatch. Using existing ID.")
            session.commit()
            session.refresh(instance)
            return instance
        else:
            # Create new instance
            params = {identifier_field: identifier_value, **(defaults or {})}
            if id_value:
                params['id'] = id_value
            instance = model(**params)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    # Ensure Branches
    branch1 = ensure_entity(db, Branch, "branch_code", "MB001", defaults={"branch_name": "Main Branch", "address": "123 Main St", "province": "Phnom Penh"}, id_value=UUID("8f6b0538-501d-42ac-be77-ab3ccfc40194"))
    branch2 = ensure_entity(db, Branch, "branch_code", "SB002", defaults={"branch_name": "Second Branch", "address": "456 Second St", "province": "Siem Reap"}, id_value=UUID("967a9866-4155-4a25-b386-7d37b49cab96"))
    branch3 = ensure_entity(db, Branch, "branch_code", "TEST123", defaults={"branch_name": "Test Branch", "address": "123 Test Street", "province": "Stung Streng"}, id_value=UUID("12345678-1234-5678-1234-567812345678"))
    print("Branches ensured.")

    # Ensure Departments
    dept1 = ensure_entity(db, Department, "department_name", "Human Resources", defaults={"description": "Manages HR operations"}, id_value=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"))
    dept2 = ensure_entity(db, Department, "department_name", "Engineering", defaults={"description": "Software and hardware development"}, id_value=UUID("b1cdef01-2345-6789-abcd-ef0123456789"))
    dept3 = ensure_entity(db, Department, "department_name", "Sales", defaults={"description": "Manages sales and customer relations"}, id_value=UUID("c2def012-3456-7890-cdef-0123456789ab"))
    print("Departments ensured.")

    # Ensure Positions
    pos1 = ensure_entity(db, Position, "title", "HR Manager", defaults={"department_id": dept1.id}, id_value=UUID("d3ef0123-4567-8901-def0-1234567890ab"))
    pos2 = ensure_entity(db, Position, "title", "Software Engineer", defaults={"department_id": dept2.id}, id_value=UUID("e4f01234-5678-9012-ef01-234567890abc"))
    pos3 = ensure_entity(db, Position, "title", "Sales Executive", defaults={"department_id": dept3.id}, id_value=UUID("f5012345-6789-0123-f012-34567890abcd"))
    print("Positions ensured.")

    # Assign data to existing users
    users = db.query(User).all()
    if users:
        # Assign to 'lc_0001'
        lc_user = db.query(User).filter(User.username == "lc_0001").first()
        if lc_user:
            lc_user.branch_id = branch1.id
            lc_user.department_id = dept1.id
            lc_user.position_id = pos1.id
            lc_user.manager_name = "Jane Doe" # type: ignore
            print(f"Assigned data to user: {lc_user.username}")

        # Assign to 'testadmin'
        testadmin_user = db.query(User).filter(User.username == "testadmin").first()
        if testadmin_user:
            testadmin_user.branch_id = branch2.id
            testadmin_user.department_id = dept2.id
            testadmin_user.position_id = pos2.id
            testadmin_user.manager_name = "John Smith" # type: ignore
            print(f"Assigned data to user: {testadmin_user.username}")
        
        # Assign to 'admin'
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            admin_user.branch_id = branch3.id
            admin_user.department_id = dept3.id
            admin_user.position_id = pos3.id
            admin_user.manager_name = "Alice Brown" # type: ignore
            print(f"Assigned data to user: {admin_user.username}")

        db.commit()
        print("User data assigned.")
    else:
        print("No users found to assign data to.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        populate_test_data(db)
        print("Test data population complete.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()