# cUPido Backend Architecture Documentation

## Overview
This is a Django-based backend API for the cUPido dating application, targeted at university students. The project uses Django REST Framework (DRF) for API development, PostgreSQL as the database, Redis for caching/verification codes, and JWT for authentication.

## 1. Implemented Functionalities

### Authentication Module (auth_app)
- **Complete User Registration**: Full registration with all required fields (names, program, gender, birth date, phone, etc.) and comprehensive validations
- **Email Verification**: Sends 6-digit verification codes via email to institutional addresses (@unipamplona.edu.co) with Redis TTL and attempt limits
- **User Creation**: Creates complete user accounts after email verification using real registration data
- **Login**: Authenticates users with JWT tokens, blocks minors, and includes session management
- **Session Management**: GET endpoint for authenticated user info and JWT token validation
- **Logout**: Individual session logout (blacklist refresh token) and global logout (invalidate all tokens)
- **Password Management**: Change password (authenticated users) and password reset via email tokens
- **Account Deactivation**: Soft delete accounts with confirmation and security checks
- **User Proxy Model**: Provides compatibility with SimpleJWT by aliasing `usuario_id` as `id`
- **Rate Limiting**: Protection against abuse on critical endpoints (registration, verification, login)

### Legacy Models (legacy_models)
- **User Model**: Comprehensive user profile with fields for personal info, preferences, and relationships
- **Supporting Models**: Gender, Orientation, Program, Location, Semester Location tables
- **Verification Model**: For email verification codes (though currently unused in favor of Redis)

### Other Apps
- **chat_app**: Placeholder for chat functionality (not implemented)
- **match_app**: Placeholder for matching algorithms (not implemented)
- **profile_app**: Placeholder for profile management (not implemented)
- **reports_app**: Placeholder for reporting features (not implemented)

## 2. Architecture

### Project Structure
```
cupido-backend/
├── config/                 # Django project settings
├── apps/                   # Django apps
│   ├── auth_app/          # Authentication module
│   ├── chat_app/          # Chat functionality (placeholder)
│   ├── match_app/         # Matching system (placeholder)
│   ├── profile_app/       # Profile management (placeholder)
│   ├── reports_app/       # Reporting features (placeholder)
│   └── legacy_models/     # Legacy database models
├── legacy_models/         # Additional legacy models
├── manage.py
├── requirements.txt
└── .env.example
```

### Technology Stack
- **Framework**: Django 5.2.7 with Django REST Framework 3.16.1
- **Database**: PostgreSQL (via dj-database-url)
- **Cache**: Redis for verification codes
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Email**: SMTP (Gmail)
- **Environment**: dotenv for configuration

### Architecture Patterns
- **App-based Architecture**: Modular Django apps for different features
- **Legacy Integration**: Proxy models to work with existing database schema
- **REST API**: DRF-based API endpoints
- **Microservices-ready**: Apps can be developed independently

## 3. Folder and File Purposes

### Root Level
- `manage.py`: Django management commands
- `requirements.txt`: Python dependencies
- `.env.example`: Environment variables template
- `README.md`: Project documentation

### config/
- `settings.py`: Django settings (database, apps, middleware, etc.)
- `urls.py`: Main URL configuration
- `wsgi.py`/`asgi.py`: WSGI/ASGI application entry points

### apps/auth_app/
- `models.py`: UsuarioProxy model for JWT compatibility
- `views/`: API views for auth operations (modular, one view per file)
  - `register_view.py`: Complete user registration with validations
  - `verify_view.py`: Email verification with code validation
  - `resend_view.py`: Resend verification codes
  - `login_view.py`: User authentication and JWT token generation
  - `session_view.py`: Authenticated user session info
  - `logout_view.py`: Individual session logout
  - `logout_all_view.py`: Global logout (all devices)
  - `password_change_view.py`: Change password for authenticated users
  - `password_reset_view.py`: Password reset request and confirmation
  - `deactivate_view.py`: Account deactivation (soft delete)
- `serializers/`: DRF serializers for data validation (modular, one serializer per file)
  - `register_serializer.py`: Complete registration validation
  - `verify_serializer.py`: Email verification validation
  - `resend_serializer.py`: Resend code validation
  - `login_serializer.py`: Login credentials validation
  - `session_serializer.py`: Session data serialization
  - `password_change_serializer.py`: Password change validation
  - `password_reset_serializer.py`: Password reset validation
  - `deactivate_serializer.py`: Account deactivation validation
  - `usuario_serializer.py`: User data serialization
- `utils/`: Reusable utilities (single responsibility principle)
  - `codes.py`: Verification code generation, validation, and management
  - `email_utils.py`: Email sending utilities (verification, password reset)
  - `redis_client.py`: Redis operations wrapper with error handling
  - `tokens.py`: JWT token utilities
  - `validators.py`: Custom validation functions (email, age, etc.)
  - `recaptcha.py`: Google reCAPTCHA verification
- `urls.py`: URL patterns for all auth endpoints
- `permissions.py`: Custom permissions (commented out)
- `admin.py`: Django admin configuration
- `apps.py`: App configuration
- `README.md`: Detailed auth module documentation


### legacy_models/
- `models.py`: Legacy database models (managed=False)
- `admin.py`: Admin registration (empty)
- `views.py`: Views (empty)
- `apps.py`: App configuration

## 4. Security & Architecture Status

### ✅ Security Improvements Implemented
- **Password Hashing**: All passwords are properly hashed using Django's make_password() and validated with check_password()
- **Comprehensive Validation**: Email domain validation, age verification (≥18), reCAPTCHA, FK existence checks
- **JWT Security**: Proper token generation, blacklist for logout, configurable expiration times
- **Rate Limiting**: Protection against abuse on registration, verification, and login endpoints
- **Redis Security**: TTL-based expiration for sensitive data, attempt limits for verification codes
- **Input Validation**: All serializers include proper validation with meaningful error messages

### ✅ Architecture Improvements Implemented
- **Modular Design**: Each view, serializer, and utility in separate files following single responsibility
- **Error Handling**: Comprehensive logging and exception handling throughout the application
- **Code Reusability**: Utility functions centralized in utils/ directory
- **Scalability**: Redis-based caching for verification codes, prepared for horizontal scaling
- **Maintainability**: Clear separation of concerns, docstrings, and consistent code style

### Code Quality Status
- **✅ Modular Organization**: Code properly separated by responsibility (views, serializers, utils)
- **✅ Error Handling**: Comprehensive logging and exception handling implemented
- **✅ Configuration**: Environment variables properly managed with validation
- **✅ Documentation**: Detailed README and architecture documentation

### Architecture Status
- **✅ Legacy Integration**: Proxy models provide compatibility with existing schema
- **✅ REST API**: Complete DRF-based API with proper HTTP status codes
- **✅ Microservices-ready**: Apps can be developed independently
- **✅ Scalability**: Redis caching and stateless JWT authentication

### Database Status
- **Legacy Models**: Managed=False for existing schema compatibility
- **✅ Data Integrity**: Application-level validations ensure data consistency
- **✅ Relationships**: Proper FK validation in serializers

## 5. API Endpoints & Examples

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Complete user registration | No |
| POST | `/api/auth/verify-email/` | Verify email with code | No |
| POST | `/api/auth/resend-code/` | Resend verification code | No |
| POST | `/api/auth/login/` | User login with JWT | No |
| GET | `/api/auth/session/` | Get authenticated user info | Yes |
| POST | `/api/auth/logout/` | Logout current session | Yes |
| POST | `/api/auth/password-change/` | Change password | Yes |
| POST | `/api/auth/password-reset/` | Request password reset | No |
| POST | `/api/auth/password-reset-confirm/` | Confirm password reset | No |
| POST | `/api/auth/deactivate/` | Deactivate account | Yes |

### cURL Examples

#### 1. User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@unipamplona.edu.co",
    "contrasena": "SecurePass123.",
    "recaptcha_token": "recaptcha_response_token",
    "nombres": "Juan",
    "apellidos": "Perez",
    "programa": 1,
    "semestreubicacion": 1,
    "genero": 1,
    "fechanacimiento": "2000-01-15",
    "numerotelefono": "3001234567",
    "tyc": true,
    "apodo": "JuanP"
  }'
```

#### 2. Email Verification
```bash
curl -X POST http://localhost:8000/api/v1/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@unipamplona.edu.co",
    "codigo": "123456"
  }'
```

#### 3. User Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.rodriguezjuajua5@unipamplona.edu.co",
    "contrasena": "SecurePass123."
  }'
```

#### 4. Get Session Info (Authenticated)
```bash
curl -X GET http://localhost:8000/api/v1/auth/session/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMzYzNDg1LCJpYXQiOjE3NjEzNjI1ODUsImp0aSI6ImQ5YzgzZjU1ZjgyYTQ4YTI4ZGU5NGY1MTgyNmU1ZTkxIiwidXNlcl9pZCI6IjExIn0.Iu10L07EUUjOR4odGWsi87sGFCxt8zGKv3SQ8NabUkU"
```

#### 5. Password Change (Authenticated)
```bash
curl -X POST http://localhost:8000/api/v1/auth/password-change/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMzYzNDg1LCJpYXQiOjE3NjEzNjI1ODUsImp0aSI6ImQ5YzgzZjU1ZjgyYTQ4YTI4ZGU5NGY1MTgyNmU1ZTkxIiwidXNlcl9pZCI6IjExIn0.Iu10L07EUUjOR4odGWsi87sGFCxt8zGKv3SQ8NabUkU" \
  -d '{
    "contrasena_actual": "SecurePass123.",
    "nueva_contrasena": "NewSecurePass123."
  }'
```

#### 6. Password Reset Request
```bash
curl -X POST http://localhost:8000/api/v1/auth/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.rodriguezjuajua5@unipamplona.edu.co"
  }'
```

#### 7. Password Reset Confirmation
```bash
curl -X POST http://localhost:8000/api/v1/auth/password-reset-confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.rodriguezjuajua5@unipamplona.edu.co",
    "token": "738623",
    "nueva_contrasena": "SecurePass123."
  }'
```

#### 8. Logout Current Session (Authenticated)
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMzYzNDg1LCJpYXQiOjE3NjEzNjI1ODUsImp0aSI6ImQ5YzgzZjU1ZjgyYTQ4YTI4ZGU5NGY1MTgyNmU1ZTkxIiwidXNlcl9pZCI6IjExIn0.Iu10L07EUUjOR4odGWsi87sGFCxt8zGKv3SQ8NabUkU" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MTk2NzU5OSwiaWF0IjoxNzYxMzYyNzk5LCJqdGkiOiJhOWZhNzAxY2Q2YzY0YWNkYjEyOGE1MGExYTZiYjBiOCIsInVzZXJfaWQiOiIxMSJ9.Ol_k59Te9_-AIPoaDG62-FZnubLJhr5C4zTtAJ6unJw"
  }'
```

#### 9. Account Deactivation (Authenticated)
```bash
curl -X POST http://localhost:8000/api/v1/auth/deactivate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMzY0NDY5LCJpYXQiOjE3NjEzNjM1NjksImp0aSI6IjdhNmY0YmMxYmVkODQ0ZWVhNDBiZDEzMThhYjI5ZDAzIiwidXNlcl9pZCI6IjUifQ.jh-zz9Y3_5IsXk_TzoBaOxWbnldcMbErdJieXNedvaM" \
  -d '{
    "contrasena": "OtraClaveSegura123",
    "confirmacion": "desactivar"
  }'
```

## 6. Future Enhancements

### Security & Features
- **2FA Implementation**: SMS/email-based two-factor authentication
- **Account Lockout**: Temporary lock after failed login attempts
- **Email Change**: Secure email address update process
- **Audit Logging**: Comprehensive user action logging

### Performance & Scalability
- **API Documentation**: Swagger/OpenAPI integration
- **Async Email**: Celery for background email processing
- **Caching**: Redis caching for user profiles and common data
- **Rate Limiting**: Advanced rate limiting with Redis

### Development & Deployment
- **Docker Support**: Containerized development and deployment
- **CI/CD Pipeline**: Automated testing and deployment
- **Monitoring**: Application performance monitoring
- **Code Standards**: Pre-commit hooks for code quality