# Admin System Documentation

This document describes the comprehensive admin system implemented for the SSO application.

## Overview

The admin system provides a complete set of tools for managing users, applications, and monitoring system health. It includes:

- **Dashboard & Analytics**: System statistics, user metrics, and activity monitoring
- **User Management**: Create, update, delete, search, and manage user accounts
- **Application Management**: Oversee OAuth applications and their configurations
- **Organization Management**: Complete management of branches, departments, and positions
- **Security Features**: Account unlocking, bulk operations, and access control

## Getting Started

### 1. Create the First Admin User

Before using the admin system, you need to create an admin user:

```bash
python create_admin.py
```

This interactive script will prompt you for:
- Admin username
- Admin email
- Full name (optional)
- Password

The script will create a user with `is_superuser=True`, granting admin privileges.

### 2. Start the Application

```bash
uvicorn app.main:app --reload
```

The admin API will be available at `http://localhost:8000/api/admin/`

## API Endpoints

### Authentication

All admin endpoints require authentication with a user that has `is_superuser=True`. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Dashboard & Statistics

#### Get Admin Dashboard
```http
GET /api/admin/dashboard
```
Returns comprehensive dashboard data including system stats, user metrics, and recent activities.

#### Get System Statistics
```http
GET /api/admin/stats/system
```
Returns overall system statistics:
- Total users, active users, verified users
- Total applications, active applications
- Security metrics (locked accounts, recent registrations)

#### Get User Statistics
```http
GET /api/admin/stats/users
```
Returns detailed user analytics:
- Registration trends over time
- User activity metrics
- Top active users

#### Get Recent Activities
```http
GET /api/admin/activities?limit=50
```
Returns recent system activities (user registrations, application creations).

### User Management

#### Search Users
```http
GET /api/admin/users?search=john&page=1&size=20&is_active=true
```
Search and filter users with pagination.

Query Parameters:
- `search`: Search by username, email, or full name
- `page`: Page number (default: 1)
- `size`: Items per page (default: 20, max: 100)
- `is_active`: Filter by active status
- `is_verified`: Filter by verification status
- `is_superuser`: Filter by admin status

#### Get User Details
```http
GET /api/admin/users/{user_id}
```
Returns detailed information about a specific user.

#### Create User
```http
POST /api/admin/users
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "New User",
  "is_active": true,
  "is_verified": true,
  "is_superuser": false
}
```

#### Update User
```http
PUT /api/admin/users/{user_id}
Content-Type: application/json

{
  "full_name": "Updated Name",
  "is_active": true,
  "password": "newpassword"  // Optional
}
```

#### Delete User
```http
DELETE /api/admin/users/{user_id}
```
Permanently deletes a user account.

#### Unlock User Account
```http
POST /api/admin/users/{user_id}/unlock
```
Unlocks a user account that was locked due to failed login attempts.

#### Bulk User Actions
```http
POST /api/admin/users/bulk-action
Content-Type: application/json

{
  "user_ids": [1, 2, 3],
  "action": "activate"  // activate, deactivate, verify, delete, unlock
}
```

### Application Management

#### Get All Applications
```http
GET /api/admin/applications?page=1&size=20&search=myapp
```
Retrieve all OAuth applications with pagination and search.

#### Get Application Details
```http
GET /api/admin/applications/{app_id}
```
Returns detailed information about a specific application.

#### Update Application
```http
PUT /api/admin/applications/{app_id}
Content-Type: application/json

{
  "name": "Updated App Name",
  "description": "Updated description",
  "redirect_uris": ["https://example.com/callback"],
  "is_active": true
}
```

#### Delete Application
```http
DELETE /api/admin/applications/{app_id}
```
Permanently deletes an OAuth application.

#### Bulk Application Actions
```http
POST /api/admin/applications/bulk-action
Content-Type: application/json

{
  "application_ids": [1, 2, 3],
  "action": "activate"  // activate, deactivate, delete
}
```

## Data Models

### System Statistics Response
```json
{
  "total_users": 150,
  "active_users": 140,
  "verified_users": 130,
  "total_applications": 25,
  "active_applications": 23,
  "locked_accounts": 2,
  "registrations_last_24h": 5,
  "registrations_last_7d": 20,
  "registrations_last_30d": 80
}
```

### User Search Response
```json
{
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "is_verified": true,
      "is_superuser": false,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

## Security Considerations

1. **Admin Access Control**: Only users with `is_superuser=True` can access admin endpoints
2. **JWT Authentication**: All requests must include a valid JWT token
3. **Rate Limiting**: Admin endpoints are subject to rate limiting
4. **Audit Logging**: All admin actions should be logged (implement as needed)
5. **Secure Passwords**: Enforce strong password policies for admin users

## Error Handling

The admin API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid or missing token)
- `403`: Forbidden (insufficient privileges)
- `404`: Not Found
- `422`: Unprocessable Entity (validation errors)
- `500`: Internal Server Error

Error responses include detailed messages:
```json
{
  "detail": "User not found"
}
```

## Development Notes

### File Structure
```
app/
├── api/
│   └── admin.py          # Admin API endpoints
├── services/
│   └── admin_service.py  # Admin business logic
├── schemas/
│   └── admin.py          # Admin data models
├── core/
│   └── auth.py           # Authentication dependencies
└── models/
    └── user.py           # User model (with is_superuser field)
```

### Key Components

1. **AdminService**: Contains all business logic for admin operations
2. **Admin Schemas**: Pydantic models for request/response validation
3. **Auth Dependencies**: JWT-based authentication with admin role checking
4. **API Routes**: RESTful endpoints following FastAPI conventions

### Testing

To test the admin system:

1. Create an admin user using `create_admin.py`
2. Obtain a JWT token by logging in
3. Use the token to access admin endpoints
4. Test various operations (CRUD, search, bulk actions)

### Future Enhancements

- **Role-based Access Control**: Implement granular permissions
- **Audit Logging**: Track all admin actions
- **Admin UI**: Build a web interface for the admin system
- **Advanced Analytics**: More detailed reporting and metrics
- **Backup/Restore**: Database backup and restore functionality
- **System Health Monitoring**: Real-time system health checks

## Troubleshooting

### Common Issues

1. **403 Forbidden**: Ensure the user has `is_superuser=True`
2. **401 Unauthorized**: Check JWT token validity and format
3. **Validation Errors**: Verify request body matches schema requirements
4. **Database Errors**: Ensure database is running and accessible

### Logs

Check application logs for detailed error information:
```bash
tail -f logs/app.log
```

## Organization Management

The admin system provides comprehensive organization structure management through branches, departments, and positions.

### Branches

Branches represent physical locations or regional offices of the organization.

#### Get All Branches
```http
GET /api/admin/branches
```
Returns a list of all branches in the organization.

**Response Example:**
```json
[
  {
    "id": "8f6b0538-501d-42ac-be77-ab3ccfc40194",
    "branch_name": "Main Branch",
    "branch_code": "MB001",
    "address": "123 Main St",
    "province": "Phnom Penh"
  }
]
```

#### Create Branch
```http
POST /api/admin/branches
```

**Request Body:**
```json
{
  "name": "New Branch",
  "code": "NB001",
  "address": "456 New Street",
  "province": "Siem Reap"
}
```

**Response:** Returns the created branch object with generated ID.

#### Update Branch
```http
PUT /api/admin/branches/{branch_id}
```

**Request Body (all fields optional):**
```json
{
  "name": "Updated Branch Name",
  "code": "UB001",
  "address": "789 Updated Street",
  "province": "Battambang"
}
```

#### Delete Branch
```http
DELETE /api/admin/branches/{branch_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Branch deleted successfully"
}
```

### Departments

Departments represent functional divisions within the organization.

#### Get All Departments
```http
GET /api/admin/departments
```

#### Create Department
```http
POST /api/admin/departments
```

**Request Body:**
```json
{
  "name": "Information Technology",
  "description": "Manages all IT infrastructure and software development"
}
```

#### Update Department
```http
PUT /api/admin/departments/{department_id}
```

**Request Body (all fields optional):**
```json
{
  "name": "Updated Department Name",
  "description": "Updated description"
}
```

#### Delete Department
```http
DELETE /api/admin/departments/{department_id}
```

### Positions

Positions represent job roles within departments.

#### Get All Positions
```http
GET /api/admin/positions
```

**Response Example:**
```json
[
  {
    "id": "36eb94e5-9f57-45fc-9d80-233d3f1a5119",
    "title": "Software Engineer",
    "department_id": "f2e447c5-5805-489c-8abb-af1c414d0cf2",
    "department_name": "IT"
  }
]
```

#### Create Position
```http
POST /api/admin/positions
```

**Request Body:**
```json
{
  "title": "Senior Developer",
  "department_id": "f2e447c5-5805-489c-8abb-af1c414d0cf2"
}
```

#### Update Position
```http
PUT /api/admin/positions/{position_id}
```

#### Delete Position
```http
DELETE /api/admin/positions/{position_id}
```

### Organization Schema Details

#### BranchResponse Schema
- `id` (string): Unique branch identifier
- `branch_name` (string): Branch name
- `branch_code` (string): Unique branch code
- `address` (string, optional): Branch address
- `province` (string, optional): Province/state

#### DepartmentResponse Schema
- `id` (string): Unique department identifier
- `department_name` (string): Department name
- `description` (string, optional): Department description

#### PositionResponse Schema
- `id` (string): Unique position identifier
- `title` (string): Position title
- `department_id` (string): Associated department ID
- `department_name` (string, optional): Department name (populated from relationship)

### Important Notes

1. **UUID Conversion**: All entity IDs are automatically converted from UUID objects to strings in API responses.

2. **Admin Access Required**: All organization management endpoints require admin privileges (`is_superuser=True`).

3. **Cascading Effects**:
   - Deleting a department may affect positions within that department
   - Deleting a branch may affect users assigned to that branch
   - Consider these relationships before deletion

4. **Validation**: All request data is validated using Pydantic schemas with appropriate field constraints.

## Support

For issues or questions about the admin system:
1. Check this documentation
2. Review the source code in the relevant files
3. Check application logs for errors
4. Ensure all dependencies are properly installed