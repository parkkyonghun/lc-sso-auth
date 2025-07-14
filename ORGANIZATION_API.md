# Organization Management API Documentation

This document provides comprehensive documentation for the organization management endpoints in the SSO Admin API.

## Overview

The Organization Management API provides endpoints for managing the organizational structure including:
- **Branches**: Physical locations or regional offices
- **Departments**: Functional divisions within the organization  
- **Positions**: Job roles within departments

All endpoints require admin authentication (`is_superuser=True`).

## Authentication

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Base URL
```
https://your-domain.com/api/admin
```

## Branches API

### Get All Branches
Retrieve a list of all branches in the organization.

```http
GET /api/admin/branches
```

**Response:**
```json
[
  {
    "id": "8f6b0538-501d-42ac-be77-ab3ccfc40194",
    "branch_name": "Main Branch",
    "branch_code": "MB001",
    "address": "123 Main St",
    "province": "Phnom Penh"
  },
  {
    "id": "967a9866-4155-4a25-b386-7d37b49cab96",
    "branch_name": "Second Branch",
    "branch_code": "SB002",
    "address": "456 Second Ave",
    "province": "Siem Reap"
  }
]
```

### Create Branch
Create a new branch with the provided information.

```http
POST /api/admin/branches
```

**Request Body:**
```json
{
  "name": "New Branch",
  "code": "NB001",
  "address": "789 New Street",
  "province": "Battambang"
}
```

**Request Schema:**
- `name` (string, required): Branch name (1-100 characters)
- `code` (string, required): Unique branch code (1-20 characters)
- `address` (string, optional): Branch address (max 300 characters)
- `province` (string, optional): Province/state (max 50 characters)

**Response:**
```json
{
  "id": "new-uuid-here",
  "branch_name": "New Branch",
  "branch_code": "NB001",
  "address": "789 New Street",
  "province": "Battambang"
}
```

### Update Branch
Update an existing branch. Only provided fields will be updated.

```http
PUT /api/admin/branches/{branch_id}
```

**Path Parameters:**
- `branch_id` (string): UUID of the branch to update

**Request Body (all fields optional):**
```json
{
  "name": "Updated Branch Name",
  "code": "UB001",
  "address": "Updated Address",
  "province": "Updated Province"
}
```

**Response:** Returns the updated branch object.

### Delete Branch
Permanently delete a branch from the system.

```http
DELETE /api/admin/branches/{branch_id}
```

**Path Parameters:**
- `branch_id` (string): UUID of the branch to delete

**Response:**
```json
{
  "success": true,
  "message": "Branch deleted successfully"
}
```

**⚠️ Warning:** Deleting a branch may affect users assigned to this branch.

## Departments API

### Get All Departments
Retrieve a list of all departments in the organization.

```http
GET /api/admin/departments
```

**Response:**
```json
[
  {
    "id": "f2e447c5-5805-489c-8abb-af1c414d0cf2",
    "department_name": "IT",
    "description": "Information Technology Department"
  },
  {
    "id": "1836b04e-3427-4f37-a968-224abf83be56",
    "department_name": "HR",
    "description": "Human Resources Department"
  }
]
```

### Create Department
Create a new department with the provided information.

```http
POST /api/admin/departments
```

**Request Body:**
```json
{
  "name": "Marketing",
  "description": "Marketing and Communications Department"
}
```

**Request Schema:**
- `name` (string, required): Department name (1-100 characters)
- `description` (string, optional): Department description (max 300 characters)

**Response:** Returns the created department object with generated ID.

### Update Department
Update an existing department. Only provided fields will be updated.

```http
PUT /api/admin/departments/{department_id}
```

**Path Parameters:**
- `department_id` (string): UUID of the department to update

**Request Body (all fields optional):**
```json
{
  "name": "Updated Department Name",
  "description": "Updated description"
}
```

### Delete Department
Permanently delete a department from the system.

```http
DELETE /api/admin/departments/{department_id}
```

**⚠️ Warning:** Deleting a department may affect positions and users assigned to this department.

## Positions API

### Get All Positions
Retrieve a list of all positions in the organization.

```http
GET /api/admin/positions
```

**Response:**
```json
[
  {
    "id": "36eb94e5-9f57-45fc-9d80-233d3f1a5119",
    "title": "Software Engineer",
    "department_id": "f2e447c5-5805-489c-8abb-af1c414d0cf2",
    "department_name": "IT"
  },
  {
    "id": "d5497925-8d15-4831-be4f-215a6ad23fba",
    "title": "HR Manager",
    "department_id": "1836b04e-3427-4f37-a968-224abf83be56",
    "department_name": "HR"
  }
]
```

### Create Position
Create a new position within a department.

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

**Request Schema:**
- `title` (string, required): Position title (1-100 characters)
- `department_id` (string, required): UUID of the department this position belongs to

### Update Position
Update an existing position. Only provided fields will be updated.

```http
PUT /api/admin/positions/{position_id}
```

**Path Parameters:**
- `position_id` (string): UUID of the position to update

**Request Body (all fields optional):**
```json
{
  "title": "Updated Position Title",
  "department_id": "new-department-uuid"
}
```

### Delete Position
Permanently delete a position from the system.

```http
DELETE /api/admin/positions/{position_id}
```

**⚠️ Warning:** Deleting a position may affect users assigned to this position.

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Branch/Department/Position not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Data Types and Constraints

### Common Fields
- **ID Fields**: All entity IDs are UUIDs automatically converted to strings
- **Name Fields**: 1-100 characters, required for creation
- **Description Fields**: Optional, max 300 characters
- **Address Fields**: Optional, max 300 characters

### Validation Rules
- Branch codes must be unique across all branches
- Department names should be unique (recommended)
- Position titles can be duplicated across different departments
- All string fields are trimmed of leading/trailing whitespace

## Implementation Notes

1. **UUID Handling**: The API automatically converts UUID database fields to string representations in responses using Pydantic model validators.

2. **Relationship Management**: When fetching positions, the department name is automatically populated from the relationship.

3. **Soft Dependencies**: The system handles cascading relationships gracefully, but consider the impact before deleting entities with dependencies.

4. **Pagination**: Currently, all endpoints return complete lists. For large organizations, consider implementing pagination.

## Testing

Use the provided test scripts to verify functionality:
- `test_branch_response.py` - Tests branch operations
- `test_create_branch.py` - Tests branch creation
- `test_all_branch_operations.py` - Comprehensive branch testing
- `test_organization_entities.py` - Tests all organization entities

## Support

For issues or questions:
1. Check the main ADMIN_SYSTEM.md documentation
2. Review the source code in `app/api/admin.py` and `app/schemas/organization.py`
3. Check application logs for detailed error information
