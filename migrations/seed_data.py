import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.application import Application
from app.models.role import Role
from app.models.permission import Permission
from app.models.branch import Branch
from app.models.department import Department
from app.models.position import Position

def seed_data():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        print("Seeding data...")

        # Add Departments
        if not db.query(Department).first():
            departments = [
                Department(department_name="IT", description="Information Technology"),
                Department(department_name="HR", description="Human Resources"),
                Department(department_name="Finance", description="Finance Department"),
            ]
            db.add_all(departments)
            db.commit()

        # Add Branches
        if not db.query(Branch).first():
            branches = [
                Branch(branch_name="Main Branch", branch_code="MB001", address="123 Main St", province="Phnom Penh"),
                Branch(branch_name="Second Branch", branch_code="SB002", address="456 Second St", province="Siem Reap"),
            ]
            db.add_all(branches)
            db.commit()

        # Add Positions
        if not db.query(Position).first():
            it_department = db.query(Department).filter_by(department_name="IT").first()
            hr_department = db.query(Department).filter_by(department_name="HR").first()
            if it_department and hr_department:
                positions = [
                    Position(title="Software Engineer", department_id=it_department.id),
                    Position(title="HR Manager", department_id=hr_department.id),
                ]
                db.add_all(positions)
                db.commit()

        # Add Users and Employees
        from app.core.security import hash_password
        from app.models.user import User
        from app.models.employee import Employee
        

        if not db.query(User).filter_by(username="admin").first():
            hashed_password = hash_password("password")
            user = User(username="admin", email="admin@example.com", hashed_password=hashed_password)
            db.add(user)
            db.commit()
        user = db.query(User).filter_by(username="admin").first()

        main_branch = db.query(Branch).filter_by(branch_code="MB001").first()
        se_position = db.query(Position).filter_by(title="Software Engineer").first()

        if not db.query(Employee).filter_by(employee_code="EMP001").first():
            main_branch = db.query(Branch).filter_by(branch_code="MB001").first()
            se_position = db.query(Position).filter_by(title="Software Engineer").first()
            if main_branch and se_position and user:
                employee = Employee(
                    user_id=user.id,
                    employee_code="EMP001",
                    full_name_khmer="បុគ្គលិក",
                    full_name_latin="Employee Name",
                    phone_number="012345678",
                    branch_id=main_branch.id,
                    position_id=se_position.id,
                    status="Active"
                )
                db.add(employee)
                db.commit()

        # Add Roles
        if not db.query(Role).first():
            roles = [
                Role(role_name="Admin", description="Administrator"),
                Role(role_name="User", description="Regular User"),
            ]
            db.add_all(roles)
            db.commit()

        # Add Permissions
        if not db.query(Permission).first():
            permissions = [
                Permission(action_name="create_user", description="Can create users"),
                Permission(action_name="delete_user", description="Can delete users"),
            ]
            db.add_all(permissions)
            db.commit()

        # Assign permissions to roles
        admin_role = db.query(Role).filter_by(role_name="Admin").first()
        if admin_role and not admin_role.permissions:
            create_user_perm = db.query(Permission).filter_by(action_name="create_user").first()
            delete_user_perm = db.query(Permission).filter_by(action_name="delete_user").first()
            if create_user_perm and delete_user_perm:
                admin_role.permissions.append(create_user_perm)
                admin_role.permissions.append(delete_user_perm)
                db.commit()

        # Assign role to user
        admin_role = db.query(Role).filter_by(role_name="Admin").first()
        user = db.query(User).filter_by(username="admin").first()
        if admin_role and user and admin_role not in user.roles:
            user.roles.append(admin_role)
            db.commit()

        # Add OAuth Application
        if not db.query(Application).first():
            import secrets
            user = db.query(User).filter_by(username="admin").first()
            if user:
                oauth_app = Application(
                    name="My Awesome App",
                    description="An awesome application.",
                    client_id=secrets.token_urlsafe(16),
                    client_secret=secrets.token_urlsafe(32),
                    redirect_uris='["http://localhost:8080/callback"]',
                    allowed_scopes='["openid", "profile", "email"]',
                    created_by=user.id
                )
                db.add(oauth_app)
                db.commit()

        print("Data seeded successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()