#!/usr/bin/env python3
"""
Setup script for roles and permissions system
This script will:
1. Run database migrations
2. Seed roles and permissions
3. Update existing admin user
"""

import sys

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from sqlalchemy import text

def run_migration():
    """Run the database migration"""
    print("Running database migration...")
    
    with engine.connect() as connection:
        # Check if permission_name column exists
        result = connection.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'permissions' AND column_name = 'permission_name'
        """))
        
        if not result.fetchone():
            print("Renaming action_name to permission_name...")
            connection.execute(text("ALTER TABLE permissions RENAME COLUMN action_name TO permission_name"))
            connection.commit()
        
        # Check if category column exists
        result = connection.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'permissions' AND column_name = 'category'
        """))
        
        if not result.fetchone():
            print("Adding category column to permissions...")
            connection.execute(text("ALTER TABLE permissions ADD COLUMN category VARCHAR(100)"))
            connection.commit()
    
    print("Migration completed successfully!")

def seed_permissions(db: Session):
    """Seed permissions into the database"""
    print("Seeding permissions...")
    
    permissions_data = [
        # User Management
        {"permission_name": "view_users", "description": "View user information", "category": "User Management"},
        {"permission_name": "create_users", "description": "Create new users", "category": "User Management"},
        {"permission_name": "edit_users", "description": "Edit user information", "category": "User Management"},
        {"permission_name": "delete_users", "description": "Delete users", "category": "User Management"},
        {"permission_name": "manage_user_roles", "description": "Assign and remove user roles", "category": "User Management"},
        {"permission_name": "view_user_activities", "description": "View user activity logs", "category": "User Management"},
        
        # Employee Management
        {"permission_name": "view_employees", "description": "View employee information", "category": "Employee Management"},
        {"permission_name": "create_employees", "description": "Create new employees", "category": "Employee Management"},
        {"permission_name": "edit_employees", "description": "Edit employee information", "category": "Employee Management"},
        {"permission_name": "delete_employees", "description": "Delete employees", "category": "Employee Management"},
        {"permission_name": "manage_employee_positions", "description": "Manage employee positions", "category": "Employee Management"},
        
        # Role & Permission Management
        {"permission_name": "view_roles", "description": "View roles", "category": "Role & Permission Management"},
        {"permission_name": "create_roles", "description": "Create new roles", "category": "Role & Permission Management"},
        {"permission_name": "edit_roles", "description": "Edit roles", "category": "Role & Permission Management"},
        {"permission_name": "delete_roles", "description": "Delete roles", "category": "Role & Permission Management"},
        {"permission_name": "view_permissions", "description": "View permissions", "category": "Role & Permission Management"},
        {"permission_name": "manage_permissions", "description": "Manage permissions", "category": "Role & Permission Management"},
        
        # Application Management
        {"permission_name": "view_applications", "description": "View applications", "category": "Application Management"},
        {"permission_name": "create_applications", "description": "Create new applications", "category": "Application Management"},
        {"permission_name": "edit_applications", "description": "Edit applications", "category": "Application Management"},
        {"permission_name": "delete_applications", "description": "Delete applications", "category": "Application Management"},
        {"permission_name": "approve_applications", "description": "Approve applications", "category": "Application Management"},
        
        # Branch Management
        {"permission_name": "view_branches", "description": "View branch information", "category": "Branch Management"},
        {"permission_name": "create_branches", "description": "Create new branches", "category": "Branch Management"},
        {"permission_name": "edit_branches", "description": "Edit branch information", "category": "Branch Management"},
        {"permission_name": "delete_branches", "description": "Delete branches", "category": "Branch Management"},
        
        # Department Management
        {"permission_name": "view_departments", "description": "View department information", "category": "Department Management"},
        {"permission_name": "create_departments", "description": "Create new departments", "category": "Department Management"},
        {"permission_name": "edit_departments", "description": "Edit department information", "category": "Department Management"},
        {"permission_name": "delete_departments", "description": "Delete departments", "category": "Department Management"},
        
        # System Administration
        {"permission_name": "view_system_stats", "description": "View system statistics", "category": "System Administration"},
        {"permission_name": "manage_system_settings", "description": "Manage system settings", "category": "System Administration"},
        {"permission_name": "view_audit_logs", "description": "View audit logs", "category": "System Administration"},
        {"permission_name": "backup_system", "description": "Perform system backups", "category": "System Administration"},
        
        # Data Management
        {"permission_name": "export_data", "description": "Export system data", "category": "Data Management"},
        {"permission_name": "import_data", "description": "Import system data", "category": "Data Management"},
        {"permission_name": "bulk_operations", "description": "Perform bulk operations", "category": "Data Management"},
    ]
    
    for perm_data in permissions_data:
        existing_permission = db.query(Permission).filter(
            Permission.permission_name == perm_data["permission_name"]
        ).first()
        
        if not existing_permission:
            permission = Permission(**perm_data)
            db.add(permission)
            print(f"Added permission: {perm_data['permission_name']}")
        else:
            # Update existing permission with category if missing
            if not existing_permission.category:
                existing_permission.category = perm_data["category"]
                print(f"Updated permission category: {perm_data['permission_name']}")
    
    db.commit()
    print("Permissions seeded successfully!")

def seed_roles(db: Session):
    """Seed roles into the database"""
    print("Seeding roles...")
    
    roles_data = [
        {
            "role_name": "Super Admin",
            "description": "Full system access with all permissions",
            "permissions": ["view_users", "create_users", "edit_users", "delete_users", "manage_user_roles", 
                           "view_user_activities", "view_employees", "create_employees", "edit_employees", 
                           "delete_employees", "manage_employee_positions", "view_roles", "create_roles", 
                           "edit_roles", "delete_roles", "view_permissions", "manage_permissions", 
                           "view_applications", "create_applications", "edit_applications", "delete_applications", 
                           "approve_applications", "view_branches", "create_branches", "edit_branches", 
                           "delete_branches", "view_departments", "create_departments", "edit_departments", 
                           "delete_departments", "view_system_stats", "manage_system_settings", "view_audit_logs", 
                           "backup_system", "export_data", "import_data", "bulk_operations"]
        },
        {
            "role_name": "System Administrator",
            "description": "System administration and user management",
            "permissions": ["view_users", "create_users", "edit_users", "delete_users", "manage_user_roles", 
                           "view_user_activities", "view_roles", "view_permissions", "view_system_stats", 
                           "manage_system_settings", "view_audit_logs", "backup_system", "export_data", "import_data"]
        },
        {
            "role_name": "HR Administrator",
            "description": "Human resources and employee management",
            "permissions": ["view_users", "create_users", "edit_users", "view_employees", "create_employees", 
                           "edit_employees", "delete_employees", "manage_employee_positions", "view_departments", 
                           "create_departments", "edit_departments", "export_data"]
        },
        {
            "role_name": "Branch Manager",
            "description": "Branch operations and local staff management",
            "permissions": ["view_users", "view_employees", "edit_employees", "view_applications", 
                           "create_applications", "edit_applications", "approve_applications", "view_branches", 
                           "edit_branches", "view_departments", "export_data"]
        },
        {
            "role_name": "Application Administrator",
            "description": "Application and workflow management",
            "permissions": ["view_users", "view_applications", "create_applications", "edit_applications", 
                           "delete_applications", "approve_applications", "view_system_stats", "export_data"]
        },
        {
            "role_name": "Department Head",
            "description": "Department management and employee oversight",
            "permissions": ["view_users", "view_employees", "edit_employees", "view_applications", 
                           "create_applications", "edit_applications", "view_departments", "edit_departments", 
                           "export_data"]
        },
        {
            "role_name": "Read Only Admin",
            "description": "Read-only access to system information",
            "permissions": ["view_users", "view_employees", "view_roles", "view_permissions", "view_applications", 
                           "view_branches", "view_departments", "view_system_stats", "view_audit_logs"]
        },
        {
            "role_name": "Employee",
            "description": "Basic employee access",
            "permissions": ["view_applications"]
        }
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.role_name == role_data["role_name"]).first()
        
        if not existing_role:
            role = Role(
                role_name=role_data["role_name"],
                description=role_data["description"]
            )
            db.add(role)
            db.flush()  # Get the role ID
            
            # Add permissions to role
            for perm_name in role_data["permissions"]:
                permission = db.query(Permission).filter(
                    Permission.permission_name == perm_name
                ).first()
                if permission:
                    role.permissions.append(permission)
            
            print(f"Added role: {role_data['role_name']} with {len(role_data['permissions'])} permissions")
        else:
            print(f"Role already exists: {role_data['role_name']}")
    
    db.commit()
    print("Roles seeded successfully!")

def update_admin_user(db: Session):
    """Update the admin user to have Super Admin role"""
    print("Updating admin user...")
    
    # Find the admin user (assuming username is 'admin')
    admin_user = db.query(User).filter(User.username == "admin").first()
    
    if admin_user:
        # Ensure admin user is superuser
        admin_user.is_superuser = True
        
        # Add Super Admin role
        super_admin_role = db.query(Role).filter(Role.role_name == "Super Admin").first()
        if super_admin_role and super_admin_role not in admin_user.roles:
            admin_user.roles.append(super_admin_role)
            print("Added Super Admin role to admin user")
        
        db.commit()
        print("Admin user updated successfully!")
    else:
        print("Admin user not found. Please create an admin user first.")

def main():
    """Main setup function"""
    print("Setting up roles and permissions system...")
    
    try:
        # Run migration
        run_migration()
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Seed permissions and roles
            seed_permissions(db)
            seed_roles(db)
            update_admin_user(db)
            
            print("\n✅ Roles and permissions system setup completed successfully!")
            print("\nAvailable roles:")
            roles = db.query(Role).all()
            for role in roles:
                print(f"  - {role.role_name}: {role.description}")
            
            print(f"\nTotal permissions: {db.query(Permission).count()}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()