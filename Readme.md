# FastAPI SSO - Single Sign-On Solution

A comprehensive Single Sign-On (SSO) solution built with FastAPI, supporting OAuth 2.0 and OpenID Connect protocols.

## Features

### 🔐 Authentication & Authorization
- **OAuth 2.0 & OpenID Connect**: Full support for modern authentication protocols
- **Multiple Grant Types**: Authorization Code, Refresh Token, Client Credentials
- **JWT Tokens**: Secure token-based authentication with RSA signing
- **Session Management**: Server-side session handling with Redis
- **Rate Limiting**: Protection against brute force attacks
- **Account Security**: Account lockout, password policies, and security monitoring

### 👥 User Management
- **User Registration & Login**: Complete user lifecycle management
- **Profile Management**: User profile updates and preferences
- **Password Management**: Secure password hashing and reset functionality
- **Account Verification**: Email-based account verification (ready for implementation)
- **Multi-factor Authentication**: Framework ready for MFA implementation

### 🔧 Application Management
- **OAuth Client Registration**: Register and manage OAuth applications
- **Client Credentials**: Secure client ID and secret management
- **Scope Management**: Fine-grained permission control
- **Redirect URI Validation**: Security through validated redirect URIs
- **Application Statistics**: Usage monitoring and analytics (framework ready)

### 🏗️ Architecture
- **Modular Design**: Clean separation of concerns with service layers
- **Database Agnostic**: SQLAlchemy ORM with PostgreSQL support
- **Caching Layer**: Redis for session management and performance
- **Docker Support**: Complete containerization with Docker Compose
- **Production Ready**: Security best practices and monitoring

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- OpenSSL (for production SSL certificates)

### 🐳 Docker Deployment (Recommended)

#### Option 1: Automated Deployment Scripts

**For Linux/macOS:**
```bash
# Clone repository
git clone <repository-url>
cd workshop

# Make deployment script executable
chmod +x deploy.sh

# Deploy for development
./deploy.sh dev

# Deploy for production
./deploy.sh prod
```

**For Windows:**
```cmd
# Clone repository
git clone <repository-url>
cd workshop

# Deploy for development
deploy.bat dev

# Deploy for production
deploy.bat prod
```

#### Option 2: Manual Docker Setup

**Development Environment:**
```bash
# Copy environment configuration
cp .env.example .env

# Start development services (SQLite + Redis)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f sso-api
```

**Production Environment:**
```bash
# Generate SSL certificates and JWT keys
mkdir -p ssl
openssl genrsa -out ssl/jwt_private_key.pem 2048
openssl rsa -in ssl/jwt_private_key.pem -pubout -out ssl/jwt_public_key.pem
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Set up environment
cp .env.example .env
# Edit .env with production settings

# Start production services (with Nginx SSL termination)
docker-compose -f docker-compose.prod.yml up -d
```

### 🔧 Deployment Management

**Check Status:**
```bash
# Linux/macOS
./deploy.sh status

# Windows
deploy.bat status

# Manual
docker-compose ps
```

**View Logs:**
```bash
# Linux/macOS
./deploy.sh logs

# Windows
deploy.bat logs

# Manual
docker-compose logs --tail=50 sso-api
```

**Stop Services:**
```bash
# Linux/macOS
./deploy.sh stop

# Windows
deploy.bat stop

# Manual
docker-compose down
```

### 🌐 Access Points

**Development (HTTP):**
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/
- **Redis**: localhost:6379

**Production (HTTPS):**
- **API Documentation**: https://localhost/docs
- **Health Check**: https://localhost/health
- **Root Endpoint**: https://localhost/
- **All HTTP traffic redirected to HTTPS**

## 🐳 Docker Architecture

### Development Stack
- **FastAPI Application**: Main SSO service
- **SQLite Database**: Lightweight file-based database
- **Redis Cache**: Session management and caching

### Production Stack
- **FastAPI Application**: Main SSO service with production settings
- **SQLite Database**: Persistent storage with volume mounting
- **Redis Cache**: High-performance caching with persistence
- **Nginx Reverse Proxy**: SSL termination, rate limiting, and load balancing

### Container Configuration

**Development (`docker-compose.yml`):**
- Simple setup for local development
- Hot reload enabled
- Debug mode active
- Direct port exposure

**Production (`docker-compose.prod.yml`):**
- Optimized for production workloads
- SSL/TLS encryption
- Rate limiting and security headers
- Health checks and resource limits
- Nginx reverse proxy with caching

### Environment Variables

Key environment variables for Docker deployment:

```bash
# Database
DATABASE_URL=sqlite:///./sso.db

# Cache
CACHE_URL=redis://redis:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_PRIVATE_KEY=your-jwt-private-key
JWT_PUBLIC_KEY=your-jwt-public-key

# Application
DEBUG=false
APP_NAME=SSO Service
APP_DESCRIPTION=FastAPI SSO and OAuth 2.0 Service
```

### Volume Management

**Development:**
- Source code mounted for hot reload
- SQLite database persisted locally

**Production:**
- SQLite data in named volume
- Redis data persistence
- SSL certificates mounted

### Security Features

**Nginx Security Headers:**
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: enabled
- Content-Security-Policy: restrictive
- HTTPS redirect for all traffic

**Rate Limiting:**
- API endpoints: 10 requests/second
- Auth endpoints: 5 requests/second
- Burst handling with queuing

## Development Setup

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with local database and cache URLs

# Initialize database
python migrations/init_db.py

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## Project Structure

```
workshop/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application setup
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── oauth.py             # OAuth 2.0 endpoints
│   │   └── applications.py      # Application management
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup
│   │   ├── cache.py             # Cache configuration
│   │   └── security.py          # Security utilities
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   └── application.py       # Application model
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py              # User schemas
│   │   └── application.py       # Application schemas
│   └── services/                 # Business logic
│       ├── __init__.py
│       ├── user_service.py       # User management
│       ├── application_service.py # App management
│       └── oauth_service.py      # OAuth logic
├── migrations/                   # Database migrations
│   ├── __init__.py
│   └── init_db.py               # Database initialization
├── templates/                    # HTML templates
│   ├── login.html
│   └── consent.html
├── static/                       # Static files (CSS, JS, images)
├── tests/                        # Test files
├── docker-compose.yml            # Docker services
├── Dockerfile                    # Application container
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user
- `PUT /auth/me` - Update current user
- `POST /auth/change-password` - Change password

### OAuth 2.0
- `GET /oauth/authorize` - Authorization endpoint
- `POST /oauth/consent` - User consent handling
- `POST /oauth/token` - Token endpoint
- `GET /oauth/userinfo` - UserInfo endpoint
- `GET /oauth/.well-known/openid-configuration` - OpenID Discovery

### Application Management
- `POST /api/applications` - Create OAuth application
- `GET /api/applications` - List user's applications
- `GET /api/applications/{id}` - Get application details
- `PUT /api/applications/{id}` - Update application
- `DELETE /api/applications/{id}` - Delete application
- `POST /api/applications/{id}/regenerate-secret` - Regenerate client secret

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- **Application**: Name, version, debug mode
- **Database**: PostgreSQL connection URL
- **Cache**: Redis connection URL
- **JWT**: Algorithm, keys, token expiration
- **Security**: Password policies, rate limiting
- **OAuth**: Authorization code and token lifetimes
- **Email**: SMTP configuration for notifications

### Security Considerations

1. **RSA Keys**: Generate unique RSA key pairs for production
2. **Secret Key**: Use a strong, unique secret key
3. **Database**: Use strong database credentials
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure allowed origins appropriately
6. **Rate Limiting**: Adjust rate limits based on your needs

## OAuth 2.0 Flow Example

### Authorization Code Flow

1. **Authorization Request**:
   ```
   GET /oauth/authorize?
     response_type=code&
     client_id=your_client_id&
     redirect_uri=http://localhost:3000/callback&
     scope=openid profile email&
     state=random_state
   ```

2. **User Login & Consent**: User logs in and grants permission

3. **Authorization Response**:
   ```
   HTTP/1.1 302 Found
   Location: http://localhost:3000/callback?code=auth_code&state=random_state
   ```

4. **Token Request**:
   ```bash
   curl -X POST http://localhost:8000/oauth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code&code=auth_code&client_id=your_client_id&client_secret=your_secret&redirect_uri=http://localhost:3000/callback"
   ```

5. **Token Response**:
   ```json
   {
     "access_token": "eyJ...",
     "token_type": "Bearer",
     "expires_in": 1800,
     "refresh_token": "eyJ...",
     "id_token": "eyJ...",
     "scope": "openid profile email"
   }
   ```

## Monitoring & Logging

### Health Checks
- Application: `GET /health`
- OAuth Service: `GET /oauth/health`

### Logging
The application uses structured logging with configurable levels:
- Request/response logging
- Security event logging
- Error tracking
- Performance monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style
- Use Black for code formatting
- Use isort for import sorting
- Follow PEP 8 guidelines
- Add type hints where appropriate

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or contributions:
- Create an issue in the repository
- Check the documentation
- Review the API documentation at `/docs`

## Roadmap

- [ ] Multi-factor Authentication (MFA)
- [ ] Social login providers (Google, GitHub, etc.)
- [x] Advanced user management (roles, permissions) - Basic user management with account status, verification, and security tracking implemented
- [ ] Audit logging and compliance features - Basic request logging implemented, comprehensive audit logging pending
- [x] Advanced rate limiting and DDoS protection - Rate limiting implemented for auth endpoints (login, register, authorize, token)
- [x] Email verification and password reset - Framework ready with database fields and token support
- [x] Application usage analytics - Basic application statistics endpoint implemented
- [ ] API versioning
- [ ] Webhook support for events
- [ ] Admin dashboard UI

## Technical Plan

This document outlines the technical plan for creating a Single Sign-On (SSO) service using FastAPI, PostgreSQL, and Dragonfly. The goal is to create a secure, scalable, and easy-to-integrate authentication and authorization provider that can act as an SDK for other applications.1. Core Concepts & Technology ChoicesSSO Flow: We will implement a flow based on the OAuth 2.0 Authorization Code Grant and OpenID Connect (OIDC). This is the industry standard for SSO.A user tries to log in to a Client Application.The Client Application redirects the user to our SSO Service for authentication.The user logs in to the SSO Service (if they aren't already).The user grants permission for the Client Application to access their identity.The SSO Service redirects the user back to the Client Application with a temporary authorization_code.The Client Application's backend securely exchanges this authorization_code with the SSO Service for an access_token and an id_token.The Client Application can now use the access_token to call protected APIs and the id_token to get user information.Technology Stack:FastAPI: A modern, high-performance Python web framework. Its automatic data validation (with Pydantic) and interactive API documentation (Swagger UI) are perfect for building a robust API that other developers will use.PostgreSQL: A powerful, open-source relational database. It will be our primary data store for persistent data like user profiles and application credentials.Dragonfly: A high-performance, in-memory datastore (Redis-compatible). We will use it for caching, session management, and storing short-lived tokens to ensure low latency.Pydantic: For data validation and settings management within FastAPI.Passlib & Bcrypt: For securely hashing and verifying user passwords.python-jose: For creating, signing, and verifying JSON Web Tokens (JWTs).2. System Architecture+-------------+      1. Redirect to Login      +---------------+      3. Login      +----------------+
|             | -----------------------------> |               | -----------------> |                |
|   Client    |                                |  SSO Service  |                    |      User      |
| Application |      5. Redirect with code     |  (FastAPI)    | <----------------- |                |
|             | <----------------------------- |               |   4. Grant Access  +----------------+
+-------------+                                +---------------+
      |  ^                                           |   |
      |  | 6. Exchange code for tokens               |   |
      |  | 7. Return tokens (Access & ID)            |   |
      v  |                                           |   |
+-------------+                                      |   |
|             |      8. Request User Info        +---v---v---+
|   Client    | --------------------------------> |           |
|   Backend   |                                   |  DB & Cache |
|             | <-------------------------------- |(Postgres & |
+-------------+     9. Return User Info           | Dragonfly)|
                                                  +-----------+

3. Database Schema (PostgreSQL)We'll need a few core tables to manage users, applications, and authorizations.users tableStores user account information.ColumnTypeConstraintsDescriptionidUUIDPrimary KeyUnique user identifier.emailVARCHAR(255)Unique, Not NullUser's email and login username.hashed_passwordVARCHAR(255)Not NullThe user's securely hashed password.full_nameVARCHAR(255)User's full name.is_activeBOOLEANDefault trueTo disable accounts.created_atTIMESTAMPNot NullWhen the account was created.updated_atTIMESTAMPNot NullWhen the account was last updated.applications tableStores information about the client applications that will use our SSO.ColumnTypeConstraintsDescriptionidUUIDPrimary KeyUnique application identifier.nameVARCHAR(255)Not NullThe display name of the application.client_idVARCHAR(255)Unique, Not NullPublic unique identifier for the app.client_secret_hashVARCHAR(255)Not NullThe app's securely hashed secret. The plain-text secret should only be displayed to the developer once upon creation and never stored directly. This column stores a bcrypt hash of that secret for verification during the token exchange.redirect_urisJSONBNot NullA JSON array of allowed callback URLs.owner_idUUIDForeign Key (users.id)The user who registered the application.created_atTIMESTAMPNot NullWhen the application was registered.4. Role of Dragonfly (In-Memory Cache)Dragonfly will be used for ephemeral data to reduce database load and improve response times.Session Management: Store user login session IDs.KEY: session:<session_id>VALUE: user_idTTL: e.g., 24 hoursAuthorization Codes: Store the short-lived authorization codes generated during the login flow.KEY: auth_code:<code>VALUE: JSON string containing user_id, client_id, redirect_uriTTL: 10 minutesRate Limiting: Track request counts for specific IPs or users to prevent abuse.KEY: rate_limit:<ip_address>:<endpoint>VALUE: countTTL: 1 minute5. API Endpoints (FastAPI)These are the core endpoints for the OIDC flow.GET /authorizeThis endpoint starts the login flow. It presents a login and consent screen to the user.Query Parameters:response_type: Must be code.client_id: The ID of the application requesting authorization.redirect_uri: The URL to redirect to after login. Must be one of the registered URIs for the client_id.scope: OIDC scopes like openid profile email.state: An opaque value used by the client to maintain state.Success Response:If the user is not logged in, returns an HTML login page.If the user is logged in, returns an HTML consent page.After consent, it redirects to the redirect_uri with code and state as query parameters.302 Redirect to redirect_uri?code=...&state=...Error Response:Redirects to redirect_uri?error=... for misconfigurations.POST /tokenThis endpoint is for confidential clients and MUST only be called from the client application's secure backend. It should never be exposed to a public client (e.g., in-browser JavaScript) as it requires the client_secret.Request Body (application/x-www-form-urlencoded):grant_type: Must be authorization_code.code: The authorization code received from the /authorize redirect.redirect_uri: The same redirect_uri used in the /authorize request.client_id: The application's client ID.client_secret: The application's client secret.Success Response (200 OK):Content-Type: application/json<!-- end list -->{
  "access_token": "eyJ...",
  "id_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}

Error Response (400 Bad Request or 401 Unauthorized):{
  "error": "invalid_grant",
  "error_description": "Authorization code is invalid or expired."
}

GET /userinfo<comment-tag id="3">A protected endpoint that returns information about the user associated with an access token.</comment-tag id="3">Headers:Authorization: Bearer <access_token>Success Response (200 OK):Content-Type: application/json<!-- end list -->{
  "sub": "user_id_uuid",
  "email": "user@example.com",
  "full_name": "Sam User"
}

Error Response (401 Unauthorized):If the token is invalid, expired, or missing.6. Development RoadmapProject Setup:Initialize a new FastAPI project.Set up virtualenv and install dependencies (fastapi, uvicorn, psycopg2-binary, redis-py, pydantic, passlib[bcrypt], python-jose).Configuration Management: Use Pydantic's BaseSettings to manage application settings (database URLs, JWT secrets, etc.) via environment variables. This separates configuration from code, which is a best practice for security and deployment flexibility.Set up Docker Compose for easy launch of PostgreSQL and Dragonfly.Core Models & Schemas:Define SQLAlchemy models for users and applications.Define Pydantic schemas for API requests and responses (e.g., UserCreate, TokenPayload, UserInfo).User Management:Implement user registration and login logic.Implement password hashing and verification.Implement /authorize Endpoint:Create the logic to validate client_id and redirect_uri.Create Jinja2 templates for the login and consent pages.Implement session management using Dragonfly.Generate and store the authorization_code in Dragonfly upon successful login and consent.Implement /token Endpoint:Implement logic to verify the authorization_code, client_id, and client_secret.On success, consume the code (delete it from Dragonfly) to prevent reuse.Generate signed JWTs using an asymmetric algorithm like RS256. The id_token should contain standard OIDC claims like iss (issuer), sub (user ID), aud (client ID), exp (expiration), and iat (issued at). The access_token can be an opaque reference token or a JWT with minimal claims like sub and scope.Implement /userinfo Endpoint:Create a dependency that validates the Authorization header.Decode the JWT to get the user_id (sub claim).Fetch and return user details from PostgreSQL.Security Hardening & Testing:Write unit and integration tests for all flows.Implement rate limiting.Ensure all database queries are sanitized.Review all security best practices for OAuth 2.0/OIDC.Documentation:Leverage FastAPI's automatic Swagger/OpenAPI documentation.Write a README.md explaining how a developer can register an application and integrate the SSO service.Plan for Building an SSO API/SDKThis document outlines the technical plan for creating a Single Sign-On (SSO) service using FastAPI, PostgreSQL, and Dragonfly. The goal is to create a secure, scalable, and easy-to-integrate authentication and authorization provider that can act as an SDK for other applications.1. Core Concepts & Technology ChoicesSSO Flow: We will implement a flow based on the OAuth 2.0 Authorization Code Grant and OpenID Connect (OIDC). This is the industry standard for SSO.A user tries to log in to a Client Application.The Client Application redirects the user to our SSO Service for authentication.The user logs in to the SSO Service (if they aren't already).The user grants permission for the Client Application to access their identity.The SSO Service redirects the user back to the Client Application with a temporary authorization_code.The Client Application's backend securely exchanges this authorization_code with the SSO Service for an access_token and an id_token.The Client Application can now use the access_token to call protected APIs and the id_token to get user information.Technology Stack:FastAPI: A modern, high-performance Python web framework. Its automatic data validation (with Pydantic) and interactive API documentation (Swagger UI) are perfect for building a robust API that other developers will use.PostgreSQL: A powerful, open-source relational database. It will be our primary data store for persistent data like user profiles and application credentials.Dragonfly: A high-performance, in-memory datastore (Redis-compatible). We will use it for caching, session management, and storing short-lived tokens to ensure low latency.Pydantic: For data validation and settings management within FastAPI.Passlib & Bcrypt: For securely hashing and verifying user passwords.python-jose: For creating, signing, and verifying JSON Web Tokens (JWTs).2. System Architecture+-------------+      1. Redirect to Login      +---------------+      3. Login      +----------------+
|             | -----------------------------> |               | -----------------> |                |
|   Client    |                                |  SSO Service  |                    |      User      |
| Application |      5. Redirect with code     |  (FastAPI)    | <----------------- |                |
|             | <----------------------------- |               |   4. Grant Access  +----------------+
+-------------+                                +---------------+
      |  ^                                           |   |
      |  | 6. Exchange code for tokens               |   |
      |  | 7. Return tokens (Access & ID)            |   |
      v  |                                           |   |
+-------------+                                      |   |
|             |      8. Request User Info        +---v---v---+
|   Client    | --------------------------------> |           |
|   Backend   |                                   |  DB & Cache |
|             | <-------------------------------- |(Postgres & |
+-------------+     9. Return User Info           | Dragonfly)|
                                                  +-----------+

3. Database Schema (PostgreSQL)We'll need a few core tables to manage users, applications, and authorizations.users tableStores user account information.ColumnTypeConstraintsDescriptionidUUIDPrimary KeyUnique user identifier.emailVARCHAR(255)Unique, Not NullUser's email and login username.hashed_passwordVARCHAR(255)Not NullThe user's securely hashed password.full_nameVARCHAR(255)User's full name.is_activeBOOLEANDefault trueTo disable accounts.created_atTIMESTAMPNot NullWhen the account was created.updated_atTIMESTAMPNot NullWhen the account was last updated.applications tableStores information about the client applications that will use our SSO.ColumnTypeConstraintsDescriptionidUUIDPrimary KeyUnique application identifier.nameVARCHAR(255)Not NullThe display name of the application.client_idVARCHAR(255)Unique, Not NullPublic unique identifier for the app.client_secret_hashVARCHAR(255)Not NullThe app's securely hashed secret. The plain-text secret should only be displayed to the developer once upon creation and never stored directly. This column stores a bcrypt hash of that secret for verification during the token exchange.redirect_urisJSONBNot NullA JSON array of allowed callback URLs.owner_idUUIDForeign Key (users.id)The user who registered the application.created_atTIMESTAMPNot NullWhen the application was registered.4. Role of Dragonfly (In-Memory Cache)Dragonfly will be used for ephemeral data to reduce database load and improve response times.Session Management: Store user login session IDs.KEY: session:<session_id>VALUE: user_idTTL: e.g., 24 hoursAuthorization Codes: Store the short-lived authorization codes generated during the login flow.KEY: auth_code:<code>VALUE: JSON string containing user_id, client_id, redirect_uriTTL: 10 minutesRate Limiting: Track request counts for specific IPs or users to prevent abuse.KEY: rate_limit:<ip_address>:<endpoint>VALUE: countTTL: 1 minute5. API Endpoints (FastAPI)These are the core endpoints for the OIDC flow.GET /authorizeThis endpoint starts the login flow. It presents a login and consent screen to the user.Query Parameters:response_type: Must be code.client_id: The ID of the application requesting authorization.redirect_uri: The URL to redirect to after login. Must be one of the registered URIs for the client_id.scope: OIDC scopes like openid profile email.state: An opaque value used by the client to maintain state.Success Response:If the user is not logged in, returns an HTML login page.If the user is logged in, returns an HTML consent page.After consent, it redirects to the redirect_uri with code and state as query parameters.302 Redirect to redirect_uri?code=...&state=...Error Response:Redirects to redirect_uri?error=... for misconfigurations.POST /tokenThis endpoint is for confidential clients and MUST only be called from the client application's secure backend. It should never be exposed to a public client (e.g., in-browser JavaScript) as it requires the client_secret.Request Body (application/x-www-form-urlencoded):grant_type: Must be authorization_code.code: The authorization code received from the /authorize redirect.redirect_uri: The same redirect_uri used in the /authorize request.client_id: The application's client ID.client_secret: The application's client secret.Success Response (200 OK):Content-Type: application/json<!-- end list -->{
  "access_token": "eyJ...",
  "id_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}

Error Response (400 Bad Request or 401 Unauthorized):{
  "error": "invalid_grant",
  "error_description": "Authorization code is invalid or expired."
}

GET /userinfo<comment-tag id="3">A protected endpoint that returns information about the user associated with an access token.</comment-tag id="3">Headers:Authorization: Bearer <access_token>Success Response (200 OK):Content-Type: application/json<!-- end list -->{
  "sub": "user_id_uuid",
  "email": "user@example.com",
  "full_name": "Sam User"
}

Error Response (401 Unauthorized):If the token is invalid, expired, or missing.6. Development RoadmapProject Setup:Initialize a new FastAPI project.Set up virtualenv and install dependencies (fastapi, uvicorn, psycopg2-binary, redis-py, pydantic, passlib[bcrypt], python-jose).Configuration Management: Use Pydantic's BaseSettings to manage application settings (database URLs, JWT secrets, etc.) via environment variables. This separates configuration from code, which is a best practice for security and deployment flexibility.Set up Docker Compose for easy launch of PostgreSQL and Dragonfly.Core Models & Schemas:Define SQLAlchemy models for users and applications.Define Pydantic schemas for API requests and responses (e.g., UserCreate, TokenPayload, UserInfo).User Management:Implement user registration and login logic.Implement password hashing and verification.Implement /authorize Endpoint:Create the logic to validate client_id and redirect_uri.Create Jinja2 templates for the login and consent pages.Implement session management using Dragonfly.Generate and store the authorization_code in Dragonfly upon successful login and consent.Implement /token Endpoint:Implement logic to verify the authorization_code, client_id, and client_secret.On success, consume the code (delete it from Dragonfly) to prevent reuse.Generate signed JWTs using an asymmetric algorithm like RS256. The id_token should contain standard OIDC claims like iss (issuer), sub (user ID), aud (client ID), exp (expiration), and iat (issued at). The access_token can be an opaque reference token or a JWT with minimal claims like sub and scope.Implement /userinfo Endpoint:Create a dependency that validates the Authorization header.Decode the JWT to get the user_id (sub claim).Fetch and return user details from PostgreSQL.Security Hardening & Testing:Write unit and integration tests for all flows.Implement rate limiting.Ensure all database queries are sanitized.Review all security best practices for OAuth 2.0/OIDC.Documentation:Leverage FastAPI's automatic Swagger/OpenAPI documentation.Write a README.md explaining how a developer can register an application and integrate the SSO service.