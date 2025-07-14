from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..api.auth import require_auth
from ..models.user import User
from ..models.branch import Branch
from ..models.department import Department
from ..models.position import Position
from ..services.admin_service import AdminService
from ..schemas.admin import (
    SystemStatsResponse, UserStatsResponse, AdminUserCreate, AdminUserUpdate,
    AdminApplicationUpdate, UserSearchResponse, ApplicationSearchResponse,
    ActivityResponse, AdminDashboardResponse, UserDetailResponse,
    ApplicationDetailResponse, BulkUserAction, BulkApplicationAction,
    AdminActionResponse, RoleResponse, PermissionResponse, RoleCreateRequest,
    PermissionCreateRequest, RoleUpdateRequest
)
from ..schemas.organization import (
    BranchResponse, DepartmentResponse, PositionResponse,
    BranchCreateRequest, BranchUpdateRequest,
    DepartmentCreateRequest, DepartmentUpdateRequest,
    PositionCreateRequest, PositionUpdateRequest,
    OrganizationDeleteResponse
)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get complete admin dashboard data"""
    admin_service = AdminService(db)

    system_stats = admin_service.get_system_stats(str(current_user.id))
    user_stats = admin_service.get_user_stats(str(current_user.id))
    recent_activities = admin_service.get_recent_activities(str(current_user.id), limit=20)

    return AdminDashboardResponse(
        system_stats=system_stats,
        user_stats=user_stats,
        recent_activities=recent_activities
    )

@router.get("/stats/system", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics"""
    admin_service = AdminService(db)
    return admin_service.get_system_stats(str(current_user.id))

@router.get("/stats/users", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get detailed user statistics"""
    admin_service = AdminService(db)
    return admin_service.get_user_stats(str(current_user.id))

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get admin statistics for dashboard (simplified endpoint for Flask admin)"""
    admin_service = AdminService(db)
    system_stats = admin_service.get_system_stats(str(current_user.id))

    return {
        "total_users": system_stats.total_users,
        "active_users": system_stats.active_users,
        "verified_users": system_stats.verified_users,
        "total_applications": system_stats.total_applications,
        "active_applications": system_stats.active_applications,
        "locked_users": system_stats.locked_users,
        "recent_registrations": system_stats.recent_registrations
    }

@router.get("/activities", response_model=ActivityResponse)
async def get_recent_activities(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get recent system activities"""
    admin_service = AdminService(db)
    activities = admin_service.get_recent_activities(str(current_user.id), limit)
    return ActivityResponse(activities=activities)

# User Management Endpoints
@router.get("/users/search", response_model=UserSearchResponse)
async def search_users(
    q: Optional[str] = Query(None, description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Search users with pagination"""
    admin_service = AdminService(db)
    skip = (page - 1) * limit
    
    users, total = admin_service.search_users(str(current_user.id), q or "", skip, limit)
    
    user_data = [{
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "is_locked": user.is_locked()
    } for user in users]
    
    return UserSearchResponse(
        users=user_data,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get detailed user information"""
    from sqlalchemy.orm import joinedload
    from ..models.user import User
    
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))
    
    # Get user with organization relationships loaded
    user = db.query(User).options(
        joinedload(User.branch),
        joinedload(User.department),
        joinedload(User.position)
    ).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "user_not_found", "detail": "User not found"}
        )
    
    return UserDetailResponse.model_validate(user)

@router.post("/users", response_model=UserDetailResponse)
async def create_user(
    user_data: AdminUserCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    admin_service = AdminService(db)
    user = admin_service.create_user_as_admin(str(current_user.id), user_data)
    return UserDetailResponse.model_validate(user)

@router.put("/users/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: str,
    user_data: AdminUserUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    admin_service = AdminService(db)
    user = admin_service.update_user_as_admin(str(current_user.id), user_id, user_data)
    return UserDetailResponse.model_validate(user)

@router.delete("/users/{user_id}", response_model=AdminActionResponse)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    admin_service = AdminService(db)
    success = admin_service.delete_user_as_admin(str(current_user.id), user_id)
    
    if success:
        return AdminActionResponse(
            success=True,
            message="User deleted successfully"
        )
    else:
        return AdminActionResponse(
            success=False,
            message="Failed to delete user"
        )

@router.post("/users/{user_id}/unlock", response_model=AdminActionResponse)
async def unlock_user(
    user_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Unlock user account"""
    admin_service = AdminService(db)
    success = admin_service.unlock_user_account(str(current_user.id), user_id)
    
    if success:
        return AdminActionResponse(
            success=True,
            message="User account unlocked successfully"
        )
    else:
        return AdminActionResponse(
            success=False,
            message="Failed to unlock user account"
        )

# Role and Permission Management Endpoints

@router.get("/users/{user_id}/roles")
async def get_user_roles(
    user_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get roles assigned to a user"""
    admin_service = AdminService(db)
    roles = admin_service.get_user_roles(str(current_user.id), user_id)
    return {"user_id": user_id, "roles": roles}

@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get permissions for a user"""
    admin_service = AdminService(db)
    permissions = admin_service.get_user_permissions(str(current_user.id), user_id)
    return {"user_id": user_id, "permissions": permissions}

@router.post("/users/{user_id}/roles/{role_name}", response_model=AdminActionResponse)
async def assign_role_to_user(
    user_id: str,
    role_name: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Assign a role to a user"""
    admin_service = AdminService(db)
    success = admin_service.assign_role_to_user(str(current_user.id), user_id, role_name)
    
    if success:
        return AdminActionResponse(
            success=True,
            message=f"Role '{role_name}' assigned to user successfully"
        )
    else:
        return AdminActionResponse(
            success=False,
            message=f"Failed to assign role '{role_name}' to user"
        )

@router.delete("/users/{user_id}/roles/{role_name}", response_model=AdminActionResponse)
async def remove_role_from_user(
    user_id: str,
    role_name: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Remove a role from a user"""
    admin_service = AdminService(db)
    success = admin_service.remove_role_from_user(str(current_user.id), user_id, role_name)
    
    if success:
        return AdminActionResponse(
            success=True,
            message=f"Role '{role_name}' removed from user successfully"
        )
    else:
        return AdminActionResponse(
            success=False,
            message=f"Failed to remove role '{role_name}' from user"
        )

@router.post("/users/bulk-action", response_model=AdminActionResponse)
async def bulk_user_action(
    action_data: BulkUserAction,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Perform bulk actions on users"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))
    
    success_count = 0
    errors = []
    
    for user_id in action_data.user_ids:
        try:
            if action_data.action == "activate":
                admin_service.user_service.activate_user(user_id)
            elif action_data.action == "deactivate":
                admin_service.user_service.deactivate_user(user_id)
            elif action_data.action == "verify":
                admin_service.user_service.verify_user(user_id)
            elif action_data.action == "delete":
                admin_service.delete_user_as_admin(str(current_user.id), user_id)
            elif action_data.action == "unlock":
                admin_service.unlock_user_account(str(current_user.id), user_id)
            else:
                errors.append(f"Unknown action: {action_data.action}")
                continue
            
            success_count += 1
        except Exception as e:
            errors.append(f"Failed to {action_data.action} user {user_id}: {str(e)}")
    
    return AdminActionResponse(
        success=success_count > 0,
        message=f"Successfully performed {action_data.action} on {success_count} users",
        affected_count=success_count,
        errors=errors if errors else None
    )

# Application Management Endpoints
@router.get("/applications", response_model=ApplicationSearchResponse)
async def get_all_applications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get all applications (admin view)"""
    admin_service = AdminService(db)
    skip = (page - 1) * limit
    
    applications, total = admin_service.get_all_applications(str(current_user.id), skip, limit)
    
    app_data = [{
        "id": str(app.id),
        "name": app.name,
        "description": app.description,
        "client_id": app.client_id,
        "is_active": app.is_active,
        "created_at": app.created_at.isoformat(),
        "created_by": app.created_by
    } for app in applications]
    
    return ApplicationSearchResponse(
        applications=app_data,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/applications/{app_id}", response_model=ApplicationDetailResponse)
async def get_application_detail(
    app_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get detailed application information"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))
    
    app = admin_service.app_service.get_application_by_id(app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "application_not_found", "detail": "Application not found"}
        )
    
    return ApplicationDetailResponse.model_validate(app)

@router.put("/applications/{app_id}", response_model=ApplicationDetailResponse)
async def update_application(
    app_id: str,
    app_data: AdminApplicationUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update application (admin only)"""
    admin_service = AdminService(db)
    app = admin_service.update_application_as_admin(str(current_user.id), app_id, app_data)
    return ApplicationDetailResponse.model_validate(app)

@router.delete("/applications/{app_id}", response_model=AdminActionResponse)
async def delete_application(
    app_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete application (admin only)"""
    admin_service = AdminService(db)
    success = admin_service.delete_application_as_admin(str(current_user.id), app_id)
    
    if success:
        return AdminActionResponse(
            success=True,
            message="Application deleted successfully"
        )
    else:
        return AdminActionResponse(
            success=False,
            message="Failed to delete application"
        )

@router.post("/applications/bulk-action", response_model=AdminActionResponse)
async def bulk_application_action(
    action_data: BulkApplicationAction,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Perform bulk actions on applications"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))
    
    success_count = 0
    errors = []
    
    for app_id in action_data.application_ids:
        try:
            if action_data.action == "activate":
                admin_service.app_service.activate_application(app_id)
            elif action_data.action == "deactivate":
                admin_service.app_service.deactivate_application(app_id)
            elif action_data.action == "delete":
                admin_service.delete_application_as_admin(str(current_user.id), app_id)
            else:
                errors.append(f"Unknown action: {action_data.action}")
                continue
            
            success_count += 1
        except Exception as e:
            errors.append(f"Failed to {action_data.action} application {app_id}: {str(e)}")
    
    return AdminActionResponse(
        success=success_count > 0,
        message=f"Successfully performed {action_data.action} on {success_count} applications",
        affected_count=success_count,
        errors=errors if errors else None
    )

# Role Management Endpoints
@router.get("/roles", response_model=List[RoleResponse])
async def get_all_roles(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get all roles"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    roles = admin_service.get_all_roles()
    return [RoleResponse(
        id=str(role.id),
        role_name=role.role_name,
        description=role.description,
        permissions=[p.permission_name for p in role.permissions]
    ) for role in roles]

@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreateRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new role"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    role = admin_service.create_role(role_data.role_name, role_data.description, role_data.permissions)
    return RoleResponse(
        id=str(role.id),
        role_name=role.role_name,
        description=role.description,
        permissions=[p.permission_name for p in role.permissions]
    )

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_data: RoleUpdateRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update a role"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    role = admin_service.update_role(role_id, role_data.dict(exclude_unset=True))
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    return RoleResponse(
        id=str(role.id),
        role_name=role.role_name,
        description=role.description,
        permissions=[p.permission_name for p in role.permissions]
    )

@router.delete("/roles/{role_id}", response_model=AdminActionResponse)
async def delete_role(
    role_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete a role"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    success = admin_service.delete_role(role_id)
    return AdminActionResponse(
        success=success,
        message="Role deleted successfully" if success else "Failed to delete role"
    )

# Permission Management Endpoints
@router.get("/permissions", response_model=List[PermissionResponse])
async def get_all_permissions(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get all permissions"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    permissions = admin_service.get_all_permissions()
    return [PermissionResponse(
        id=str(perm.id),
        permission_name=perm.permission_name,
        description=perm.description
    ) for perm in permissions]

@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreateRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new permission"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    permission = admin_service.create_permission(
        permission_data.permission_name,
        permission_data.description
    )
    return PermissionResponse(
        id=str(permission.id),
        permission_name=permission.permission_name,
        description=permission.description
    )

@router.delete("/permissions/{permission_id}", response_model=AdminActionResponse)
async def delete_permission(
    permission_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete a permission"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    success = admin_service.delete_permission(permission_id)
    return AdminActionResponse(
        success=success,
        message="Permission deleted successfully" if success else "Failed to delete permission"
    )

# Organization Structure Endpoints
@router.get("/branches", response_model=List[BranchResponse])
async def get_all_branches(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get all branches

    Returns a list of all branches in the organization.
    Requires admin privileges.
    """
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    branches = db.query(Branch).all()
    
    # Manual conversion to ensure UUID is properly converted to string
    return [
        BranchResponse(
            id=str(branch.id),
            branch_name=branch.branch_name,
            branch_code=branch.branch_code,
            address=branch.address,
            province=branch.province
        ) for branch in branches
    ]

@router.post("/branches", response_model=BranchResponse)
async def create_branch(
    branch_data: BranchCreateRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Create a new branch

    Creates a new branch with the provided information.
    Requires admin privileges.

    - **name**: Branch name (required)
    - **code**: Unique branch code (required)
    - **address**: Branch address (optional)
    - **province**: Province/state (optional)
    """
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    branch = Branch(
        branch_name=branch_data.name,
        branch_code=branch_data.code,
        address=branch_data.address,
        province=branch_data.province
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return BranchResponse.model_validate(branch)

@router.put("/branches/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: str,
    branch_data: BranchUpdateRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Update a branch

    Updates an existing branch with the provided information.
    Only provided fields will be updated.
    Requires admin privileges.

    - **name**: Branch name (optional)
    - **code**: Unique branch code (optional)
    - **address**: Branch address (optional)
    - **province**: Province/state (optional)
    """
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    if branch_data.name is not None:
        branch.branch_name = branch_data.name
    if branch_data.code is not None:
        branch.branch_code = branch_data.code
    if branch_data.address is not None:
        branch.address = branch_data.address
    if branch_data.province is not None:
        branch.province = branch_data.province

    db.commit()
    db.refresh(branch)
    return BranchResponse.model_validate(branch)

@router.delete("/branches/{branch_id}", response_model=OrganizationDeleteResponse)
async def delete_branch(
    branch_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Delete a branch

    Permanently deletes a branch from the system.
    This action cannot be undone.
    Requires admin privileges.

    **Warning**: Deleting a branch may affect users assigned to this branch.
    """
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    db.delete(branch)
    db.commit()
    return OrganizationDeleteResponse(
        success=True,
        message="Branch deleted successfully"
    )

@router.get("/departments", response_model=List[DepartmentResponse])
async def get_all_departments(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get all departments

    Returns a list of all departments in the organization.
    Requires admin privileges.
    """
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    departments = db.query(Department).all()
    
    # Manual conversion to ensure UUID is properly converted to string
    return [
        DepartmentResponse(
            id=str(dept.id),
            department_name=dept.department_name,
            description=dept.description
        ) for dept in departments
    ]

@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreateRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Create a new department

    Creates a new department with the provided information.
    Requires admin privileges.

    - **name**: Department name (required)
    - **description**: Department description (optional)
    """
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    department = Department(
        department_name=department_data.name,
        description=department_data.description
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    return DepartmentResponse.model_validate(department)

@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdateRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Update a department

    Updates an existing department with the provided information.
    Only provided fields will be updated.
    Requires admin privileges.

    - **name**: Department name (optional)
    - **description**: Department description (optional)
    """
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if department_data.name is not None:
        department.department_name = department_data.name
    if department_data.description is not None:
        department.description = department_data.description

    db.commit()
    db.refresh(department)
    return DepartmentResponse.model_validate(department)

@router.delete("/departments/{department_id}", response_model=OrganizationDeleteResponse)
async def delete_department(
    department_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Delete a department

    Permanently deletes a department from the system.
    This action cannot be undone.
    Requires admin privileges.

    **Warning**: Deleting a department may affect positions and users assigned to this department.
    """
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    db.delete(department)
    db.commit()
    return OrganizationDeleteResponse(
        success=True,
        message="Department deleted successfully"
    )

@router.get("/positions", response_model=List[PositionResponse])
async def get_all_positions(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get all positions"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    positions = db.query(Position).all()
    
    # Manual conversion to ensure UUID is properly converted to string
    return [
        PositionResponse(
            id=str(pos.id),
            title=pos.title,
            department_id=str(pos.department_id) if pos.department_id else None,
            department_name=pos.department.department_name if pos.department else None
        ) for pos in positions
    ]

@router.post("/positions", response_model=PositionResponse)
async def create_position(
    position_data: dict,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new position"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    position = Position(
        title=position_data["title"],
        department_id=position_data["department_id"]
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return PositionResponse.model_validate(position)

@router.put("/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: str,
    position_data: dict,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update a position"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    if "title" in position_data:
        position.title = position_data["title"]
    if "department_id" in position_data:
        position.department_id = position_data["department_id"]
    
    db.commit()
    db.refresh(position)
    return PositionResponse.model_validate(position)

@router.delete("/positions/{position_id}")
async def delete_position(
    position_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete a position"""
    admin_service = AdminService(db)
    admin_service.verify_admin_access(str(current_user.id))

    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    db.delete(position)
    db.commit()
    return {"success": True, "message": "Position deleted successfully"}
