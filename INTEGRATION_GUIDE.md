# Flask Admin + FastAPI Backend Integration Guide

This guide explains how to use the integrated Flask admin frontend with the FastAPI backend for real data management.

## 🏗️ Architecture Overview

```
┌─────────────────┐    HTTP/JSON API    ┌──────────────────┐
│  Flask Admin    │ ◄─────────────────► │  FastAPI Backend │
│  Frontend       │                     │                  │
│  (Port 5000)    │                     │  (Port 8000)     │
└─────────────────┘                     └──────────────────┘
         │                                        │
         │                                        │
         ▼                                        ▼
┌─────────────────┐                     ┌──────────────────┐
│  HTML Templates │                     │  PostgreSQL DB   │
│  Static Assets  │                     │  Redis Cache     │
└─────────────────┘                     └──────────────────┘
```

## 🚀 Quick Start

### 1. Setup the Integration

```bash
# Run the setup script
python setup_integration.py
```

This will:
- Create database tables
- Create an admin user
- Set up sample roles and permissions
- Verify the setup

### 2. Start the Services

**Terminal 1 - FastAPI Backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Flask Admin Frontend:**
```bash
cd flask_admin
python app.py
```

### 3. Test the Integration

```bash
python test_integration.py
```

### 4. Access the Admin Interface

Open your browser and go to: http://localhost:5000

Login with the admin credentials you created during setup.

## 📋 Features

### ✅ Implemented Features

- **Authentication**: JWT-based authentication between Flask and FastAPI
- **User Management**: Full CRUD operations for users
- **Role & Permission Management**: Create and manage roles and permissions
- **Application Management**: OAuth application management
- **Dashboard**: Real-time statistics and monitoring
- **Error Handling**: Comprehensive error handling and validation

### 🔄 Data Flow

1. **User Login**: Flask admin authenticates with FastAPI and receives JWT token
2. **API Calls**: All Flask admin operations call FastAPI endpoints with JWT token
3. **Data Processing**: FastAPI processes requests and interacts with database
4. **Response**: FastAPI returns JSON data to Flask admin for display

## 🛠️ API Endpoints Integration

### Authentication Endpoints
- `POST /auth/login` - User authentication
- `POST /auth/logout` - User logout

### Admin Endpoints
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/users/search` - Search users with pagination
- `POST /api/admin/users` - Create new user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/roles` - List all roles
- `POST /api/admin/roles` - Create new role
- `GET /api/admin/permissions` - List all permissions
- `GET /api/admin/applications` - List OAuth applications

## 🔧 Configuration

### Flask Admin Configuration (`flask_admin/app.py`)

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    FASTAPI_BASE_URL = os.environ.get('FASTAPI_BASE_URL') or 'http://localhost:8000'
    WTF_CSRF_ENABLED = True
```

### FastAPI Configuration (`app/core/config.py`)

```python
class Settings(BaseSettings):
    app_name: str = "SSO Service"
    database_url: str = "sqlite:///./sso.db"
    cache_url: str = "redis://localhost:6379"
    jwt_algorithm: str = "RS256"
    # ... other settings
```

## 🔐 Security Features

### Authentication
- JWT tokens with RSA signing
- Session management with Redis
- Automatic token refresh
- Secure cookie handling

### Authorization
- Role-based access control
- Permission-based operations
- Admin-only endpoints
- Rate limiting

### Data Validation
- Pydantic schemas for API validation
- WTForms validation in Flask
- SQL injection prevention
- XSS protection

## 🧪 Testing

### Manual Testing
1. Run `python test_integration.py`
2. Check all endpoints are working
3. Verify authentication flow
4. Test CRUD operations

### Test Scenarios
- User login/logout
- User creation/editing/deletion
- Role and permission management
- Application management
- Error handling
- Session management

## 🐛 Troubleshooting

### Common Issues

**1. Connection Refused**
```
Error: Connection error: Connection refused
```
**Solution**: Ensure FastAPI backend is running on port 8000

**2. Authentication Failed**
```
Error: Unauthorized - Admin access required
```
**Solution**: Ensure user has `is_superuser=True` in database

**3. Database Errors**
```
Error: Database connection failed
```
**Solution**: Run `python setup_integration.py` to initialize database

**4. Missing Dependencies**
```
Error: Module not found
```
**Solution**: Install requirements: `pip install -r requirements.txt`

### Debug Mode

Enable debug mode for detailed error messages:

**FastAPI:**
```bash
uvicorn app.main:app --reload --log-level debug
```

**Flask:**
```python
app.config['DEBUG'] = True
```

## 📁 File Structure

```
workshop/
├── app/                          # FastAPI Backend
│   ├── api/
│   │   ├── admin.py             # Admin API endpoints
│   │   ├── auth.py              # Authentication endpoints
│   │   └── oauth.py             # OAuth endpoints
│   ├── services/
│   │   ├── admin_service.py     # Admin business logic
│   │   └── user_service.py      # User management
│   └── schemas/
│       └── admin.py             # Admin API schemas
├── flask_admin/                  # Flask Frontend
│   ├── app.py                   # Main Flask application
│   └── templates/               # HTML templates
├── setup_integration.py         # Setup script
├── test_integration.py          # Integration tests
└── INTEGRATION_GUIDE.md         # This file
```

## 🔄 Development Workflow

1. **Backend Changes**: Modify FastAPI endpoints in `app/api/`
2. **Frontend Changes**: Update Flask routes in `flask_admin/app.py`
3. **Test Changes**: Run `python test_integration.py`
4. **Deploy**: Use Docker Compose for production deployment

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OAuth 2.0 Specification](https://tools.ietf.org/html/rfc6749)
- [JWT Tokens](https://jwt.io/)

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run the integration test script
3. Check application logs
4. Verify database and cache connections
