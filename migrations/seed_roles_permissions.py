import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


def seed_comprehensive_roles_permissions():
    """Seed comprehensive roles and permissions for the admin system"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        print("Seeding comprehensive roles and permissions...")
        
        # Define comprehensive permissions by category
        permissions_data = [
            # User Management
            {"name": "view_users", "description": "Can view user profiles and lists", "category": "User Management"},
            {"name": "create_users", "description": "Can create new user accounts", "category": "User Management"},
            {"name": "edit_users", "description": "Can edit user profiles and information", "category": "User Management"},
            {"name": "delete_users", "description": "Can delete user accounts", "category": "User Management"},
            {"name": "manage_user_roles", "description": "Can assign/remove roles from users", "category": "User Management"},
            {"name": "reset_user_passwords", "description": "Can reset user passwords", "category": "User Management"},
            {"name": "lock_unlock_users", "description": "Can lock/unlock user accounts", "category": "User Management"},
            
            # Employee Management
            {"name": "view_employees", "description": "Can view employee records", "category": "Employee Management"},
            {"name": "create_employees", "description": "Can create new employee records", "category": "Employee Management"},
            {"name": "edit_employees", "description": "Can edit employee information", "category": "Employee Management"},
            {"name": "delete_employees", "description": "Can delete employee records", "category": "Employee Management"},
            {"name": "manage_employee_status", "description": "Can change employee status (active/inactive)", "category": "Employee Management"},
            
            # Department Management
            {"name": "view_departments", "description": "Can view department information", "category": "Department Management"},
            {"name": "create_departments", "description": "Can create new departments", "category": "Department Management"},
            {"name": "edit_departments", "description": "Can edit department information", "category": "Department Management"},
            {"name": "delete_departments", "description": "Can delete departments", "category": "Department Management"},
            
            # Branch Management
            {"name": "view_branches", "description": "Can view branch information", "category": "Branch Management"},
            {"name": "create_branches", "description": "Can create new branches", "category": "Branch Management"},
            {"name": "edit_branches", "description": "Can edit branch information", "category": "Branch Management"},
            {"name": "delete_branches", "description": "Can delete branches", "category": "Branch Management"},
            
            # Position Management
            {"name": "view_positions", "description": "Can view position information", "category": "Position Management"},
            {"name": "create_positions", "description": "Can create new positions", "category": "Position Management"},
            {"name": "edit_positions", "description": "Can edit position information", "category": "Position Management"},
            {"name": "delete_positions", "description": "Can delete positions", "category": "Position Management"},
            
            # Application Management
            {"name": "view_applications", "description": "Can view OAuth applications", "category": "Application Management"},
            {"name": "create_applications", "description": "Can create new OAuth applications", "category": "Application Management"},
            {"name": "edit_applications", "description": "Can edit OAuth applications", "category": "Application Management"},
            {"name": "delete_applications", "description": "Can delete OAuth applications", "category": "Application Management"},
            {"name": "manage_application_secrets", "description": "Can regenerate application secrets", "category": "Application Management"},
            
            # Role & Permission Management
            {"name": "view_roles", "description": "Can view roles and permissions", "category": "Role Management"},
            {"name": "create_roles", "description": "Can create new roles", "category": "Role Management"},
            {"name": "edit_roles", "description": "Can edit roles and their permissions", "category": "Role Management"},
            {"name": "delete_roles", "description": "Can delete roles", "category": "Role Management"},
            {"name": "manage_permissions", "description": "Can manage system permissions", "category": "Role Management"},
            
            # System Administration
            {"name": "view_system_logs", "description": "Can view system logs and audit trails", "category": "System Administration"},
            {"name": "manage_system_settings", "description": "Can modify system settings", "category": "System Administration"},
            {"name": "backup_restore", "description": "Can perform backup and restore operations", "category": "System Administration"},
            {"name": "view_analytics", "description": "Can view system analytics and reports", "category": "System Administration"},
            
            # Data Management
            {"name": "export_data", "description": "Can export data from the system", "category": "Data Management"},
            {"name": "import_data", "description": "Can import data into the system", "category": "Data Management"},
            {"name": "bulk_operations", "description": "Can perform bulk operations on data", "category": "Data Management"},
        ]
        
        # Create permissions
        created_permissions = {}
        for perm_data in permissions_data:
            existing_perm = db.query(Permission).filter(
                Permission.permission_name == perm_data["name"]
            ).first()
            
            if not existing_perm:
                permission = Permission(
                    permission_name=perm_data["name"],
                    description=perm_data["description"],
                    category=perm_data["category"]
                )
                db.add(permission)
                db.flush()  # Flush to get the ID
                created_permissions[perm_data["name"]] = permission
                print(f"Created permission: {perm_data['name']}")
            else:
                created_permissions[perm_data["name"]] = existing_perm
                print(f"Permission already exists: {perm_data['name']}")
        
        db.commit()
        
        # Define comprehensive roles with their permissions
        roles_data = [
            {
                "name": "Super Admin",
                "description": "Full system access with all permissions",
                "permissions": [perm["name"] for perm in permissions_data]  # All permissions
            },
            {
                "name": "System Administrator",
                "description": "System administration and user management",
                "permissions": [
                    "view_users", "create_users", "edit_users", "delete_users", "manage_user_roles",
                    "reset_user_passwords", "lock_unlock_users", "view_employees", "create_employees",
                    "edit_employees", "delete_employees", "manage_employee_status", "view_departments",
                    "create_departments", "edit_departments", "delete_departments", "view_branches",
                    "create_branches", "edit_branches", "delete_branches", "view_positions",
                    "create_positions", "edit_positions", "delete_positions", "view_applications",
                    "create_applications", "edit_applications", "delete_applications",
                    "manage_application_secrets", "view_roles", "create_roles", "edit_roles",
                    "delete_roles", "manage_permissions", "view_system_logs", "manage_system_settings",
                    "backup_restore", "view_analytics", "export_data", "import_data", "bulk_operations"
                ]
            },
            {
                "name": "HR Administrator",
                "description": "Human resources management with employee focus",
                "permissions": [
                    "view_users", "create_users", "edit_users", "reset_user_passwords",
                    "view_employees", "create_employees", "edit_employees", "delete_employees",
                    "manage_employee_status", "view_departments", "edit_departments",
                    "view_branches", "edit_branches", "view_positions", "create_positions",
                    "edit_positions", "delete_positions", "export_data", "import_data"
                ]
            },
            {
                "name": "Branch Manager",
                "description": "Branch-level management with limited administrative access",
                "permissions": [
                    "view_users", "edit_users", "view_employees", "create_employees",
                    "edit_employees", "manage_employee_status", "view_departments",
                    "view_branches", "edit_branches", "view_positions", "export_data"
                ]
            },
            {
                "name": "Application Administrator",
                "description": "OAuth application management",
                "permissions": [
                    "view_users", "view_applications", "create_applications",
                    "edit_applications", "delete_applications", "manage_application_secrets",
                    "view_analytics", "export_data"
                ]
            },
            {
                "name": "Department Head",
                "description": "Department-level management",
                "permissions": [
                    "view_users", "view_employees", "edit_employees", "manage_employee_status",
                    "view_departments", "edit_departments", "view_positions", "create_positions",
                    "edit_positions", "export_data"
                ]
            },
            {
                "name": "Read Only Admin",
                "description": "View-only access to all administrative data",
                "permissions": [
                    "view_users", "view_employees", "view_departments", "view_branches",
                    "view_positions", "view_applications", "view_roles", "view_system_logs",
                    "view_analytics", "export_data"
                ]
            },
            {
                "name": "Employee",
                "description": "Basic employee access",
                "permissions": [
                    "view_users", "view_employees", "view_departments", "view_branches", "view_positions"
                ]
            }
        ]
        
        # Create roles and assign permissions
        created_roles = {}
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.role_name == role_data["name"]).first()
            
            if not existing_role:
                role = Role(
                    role_name=role_data["name"],
                    description=role_data["description"]
                )
                db.add(role)
                db.flush()  # Flush to get the ID
                created_roles[role_data["name"]] = role
                print(f"Created role: {role_data['name']}")
            else:
                created_roles[role_data["name"]] = existing_role
                print(f"Role already exists: {role_data['name']}")
                # Clear existing permissions to update them
                existing_role.permissions.clear()
            
            # Assign permissions to role
            role_obj = created_roles[role_data["name"]]
            for perm_name in role_data["permissions"]:
                if perm_name in created_permissions:
                    permission = created_permissions[perm_name]
                    if permission not in role_obj.permissions:
                        role_obj.permissions.append(permission)
        
        db.commit()
        
        # Update existing admin user to have Super Admin role if exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            super_admin_role = created_roles.get("Super Admin")
            if super_admin_role and super_admin_role not in admin_user.roles:
                admin_user.roles.clear()  # Remove old roles
                admin_user.roles.append(super_admin_role)
                admin_user.is_superuser = True  # Ensure superuser flag is set
                db.commit()
                print("Updated admin user with Super Admin role")
        
        print("\nRoles and permissions seeded successfully!")
        print(f"Created {len(created_permissions)} permissions")
        print(f"Created {len(created_roles)} roles")
        
        # Print summary
        print("\n=== ROLES SUMMARY ===")
        for role_name, role in created_roles.items():
            print(f"\n{role_name}:")
            print(f"  Description: {role.description}")
            print(f"  Permissions ({len(role.permissions)}): {', '.join([p.permission_name for p in role.permissions[:5]])}{'...' if len(role.permissions) > 5 else ''}")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_comprehensive_roles_permissions()