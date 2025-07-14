# Flask Admin Frontend for SSO System

A modern web-based admin interface for managing the SSO (Single Sign-On) system. This Flask application provides a user-friendly dashboard to manage users, OAuth applications, and monitor system activity.

## Features

### 🎯 Dashboard & Analytics
- **System Overview**: Real-time statistics and metrics
- **User Analytics**: Registration trends, active users, login patterns
- **Application Metrics**: OAuth app usage and status monitoring
- **Recent Activity**: Latest user registrations and login attempts

### 👥 User Management
- **User Listing**: Paginated view with search and filtering
- **User Creation**: Add new users with role assignment
- **User Editing**: Update user information and permissions
- **Bulk Operations**: Activate, deactivate, or delete multiple users
- **User Details**: Comprehensive user profile and activity history

### 🔧 Application Management
- **OAuth Apps**: Manage OAuth 2.0 applications
- **Client Credentials**: Generate and manage client IDs and secrets
- **Redirect URIs**: Configure allowed callback URLs
- **Scope Management**: Set default OAuth scopes
- **App Status**: Enable/disable applications

### 🔐 Security Features
- **Admin Authentication**: Secure login for administrators
- **Role-based Access**: Superuser permissions required
- **Session Management**: Secure JWT token handling
- **CSRF Protection**: Form security with Flask-WTF

## Prerequisites

- Python 3.8+
- FastAPI backend running on `http://localhost:8000`
- Admin user created in the SSO system

## Installation

1. **Navigate to the Flask admin directory**:
   ```bash
   cd flask_admin
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional):
   ```bash
   # Windows
   set FLASK_ENV=development
   set SECRET_KEY=your-secret-key-here
   set FASTAPI_BASE_URL=http://localhost:8000
   
   # macOS/Linux
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key-here
   export FASTAPI_BASE_URL=http://localhost:8000
   ```

## Running the Application

1. **Ensure the FastAPI backend is running**:
   ```bash
   # In the main project directory
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start the Flask admin frontend**:
   ```bash
   # In the flask_admin directory
   python app.py
   ```

3. **Access the admin interface**:
   - Open your browser and go to: `http://localhost:5000`
   - Login with your admin credentials

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key` | Flask secret key for sessions |
| `FASTAPI_BASE_URL` | `http://localhost:8000` | Backend API base URL |
| `FLASK_ENV` | `production` | Flask environment mode |

### Backend Integration

The Flask frontend communicates with the FastAPI backend through REST API calls:

- **Authentication**: `/api/admin/login`
- **Dashboard**: `/api/admin/dashboard`
- **Users**: `/api/admin/users/*`
- **Applications**: `/api/admin/applications/*`

## Usage Guide

### First Time Setup

1. **Create an admin user** (if not already done):
   ```bash
   # In the main project directory
   python create_admin.py
   ```

2. **Start both services**:
   - FastAPI backend on port 8000
   - Flask frontend on port 5000

3. **Login to the admin panel**:
   - Navigate to `http://localhost:5000`
   - Use your admin credentials

### Managing Users

1. **View Users**: Click "Users" in the sidebar
2. **Create User**: Click "New User" button
3. **Edit User**: Click the edit icon next to any user
4. **Bulk Actions**: Select multiple users and choose an action
5. **Search/Filter**: Use the search bar and status filters

### Managing Applications

1. **View Apps**: Click "Applications" in the sidebar
2. **Create App**: Click "New Application" button
3. **Configure**: Set redirect URIs, scopes, and permissions
4. **Monitor**: View app status and usage statistics

### Dashboard Insights

- **Statistics Cards**: Quick overview of system metrics
- **Recent Activity**: Latest user and application events
- **Charts**: Visual representation of trends and patterns
- **Quick Actions**: Fast access to common tasks

## API Integration

### Authentication Flow

```python
# Login request
POST /api/admin/login
{
    "username": "admin",
    "password": "password"
}

# Response
{
    "access_token": "jwt-token",
    "token_type": "bearer",
    "user": {...}
}
```

### Making Authenticated Requests

```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.get(
    f"{FASTAPI_BASE_URL}/api/admin/users",
    headers=headers
)
```

## Development

### Project Structure

```
flask_admin/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── templates/            # Jinja2 templates
    ├── base.html         # Base template with navigation
    ├── login.html        # Admin login page
    ├── dashboard.html    # Main dashboard
    ├── users.html        # User management
    ├── user_form.html    # User creation/editing
    └── applications.html # Application management
```

### Adding New Features

1. **Create new routes** in `app.py`
2. **Add templates** in the `templates/` directory
3. **Update navigation** in `base.html`
4. **Add API calls** using the `FastAPIClient` class

### Styling and UI

- **Bootstrap 5**: Modern responsive framework
- **Bootstrap Icons**: Comprehensive icon library
- **Chart.js**: Interactive charts and graphs
- **Custom CSS**: Additional styling in templates

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Ensure FastAPI backend is running on port 8000
   - Check `FASTAPI_BASE_URL` configuration

2. **Login Failed**:
   - Verify admin user exists and has superuser privileges
   - Check username/password combination

3. **Template Not Found**:
   - Ensure all template files are in the `templates/` directory
   - Check file names and paths

4. **CSRF Token Missing**:
   - Ensure `SECRET_KEY` is set
   - Check form includes `{{ form.hidden_tag() }}`

### Debug Mode

Run in debug mode for detailed error messages:

```bash
export FLASK_ENV=development  # or set FLASK_ENV=development on Windows
python app.py
```

### Logs

Check console output for:
- API request/response details
- Authentication status
- Error messages and stack traces

## Security Considerations

- **Change default SECRET_KEY** in production
- **Use HTTPS** for production deployments
- **Implement rate limiting** for login attempts
- **Regular security updates** for dependencies
- **Monitor admin access** and audit logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the SSO system and follows the same licensing terms.