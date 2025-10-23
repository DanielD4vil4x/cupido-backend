# cUPido Backend Architecture Documentation

## Overview
This is a Django-based backend API for the cUPido dating application, targeted at university students. The project uses Django REST Framework (DRF) for API development, PostgreSQL as the database, Redis for caching/verification codes, and JWT for authentication.

## 1. Implemented Functionalities

### Authentication Module (auth_app)
- **Email Verification**: Sends 6-digit verification codes via email to institutional addresses (@unipamplona.edu.co)
- **User Registration**: Creates user accounts after email verification
- **Login**: Authenticates users and issues JWT tokens
- **User Proxy Model**: Provides compatibility with SimpleJWT by aliasing `usuario_id` as `id`

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
- `views/`: API views for auth operations
  - `auth.py`: Login and registration views
  - `verification.py`: Email verification view
- `serializers/`: DRF serializers for data validation
- `urls.py`: URL patterns for auth endpoints
- `permissions.py`: Custom permissions (commented out)
- `admin.py`: Django admin configuration
- `apps.py`: App configuration
- `README.md`: Detailed auth module documentation

### apps/[other_apps]/
- `models.py`: Database models (empty placeholders)
- `views.py`: API views (empty placeholders)
- `admin.py`: Admin configuration (empty)
- `apps.py`: App configuration
- `tests.py`: Test files (empty)
- `migrations/`: Database migrations

### legacy_models/
- `models.py`: Legacy database models (managed=False)
- `admin.py`: Admin registration (empty)
- `views.py`: Views (empty)
- `apps.py`: App configuration

## 4. Bad Practices Analysis

### Security Issues
- **Plain Text Passwords**: Passwords stored in plain text in the database (line 64 in legacy_models/models.py)
- **No Password Hashing**: Registration stores passwords directly without hashing
- **Weak Authentication**: Login compares plain text passwords (line 92 in auth.py)
- **No Password Validation**: No enforcement of password strength requirements
- **Email Verification Bypass**: No actual age verification or other validations mentioned in README

### Code Quality Issues
- **Mixed Languages**: Code comments and documentation in Spanish, but code in English
- **Inconsistent Naming**: Mix of Spanish field names (nombres, apellidos) and English (email, password)
- **Hardcoded Values**: Email domain hardcoded in verification view
- **Global Redis Connection**: Redis connection created globally in views
- **No Error Handling**: Basic exception handling in registration
- **Commented Code**: Permissions file has commented-out code

### Architecture Issues
- **Legacy Dependency**: Heavy reliance on unmanaged legacy models
- **Incomplete Implementation**: Most apps are just placeholders
- **No Tests**: Test files are empty
- **No Documentation**: API documentation missing (no Swagger/OpenAPI)
- **Environment Handling**: No validation of required environment variables

### Database Issues
- **Managed=False**: Legacy models not managed by Django migrations
- **No Relationships**: Missing foreign key constraints in some places
- **Data Integrity**: No database-level validations

## 5. Recommendations

### Security Improvements
1. **Implement Proper Password Hashing**:
   - Use Django's built-in password hashing
   - Update legacy model to use hashed passwords
   - Migrate existing plain text passwords

2. **Add Password Validation**:
   - Implement Django's password validators
   - Add custom validators for institutional requirements

3. **Improve Authentication**:
   - Add rate limiting for login attempts
   - Implement account lockout after failed attempts
   - Add password reset functionality

4. **Email Security**:
   - Use secure email service (not Gmail SMTP)
   - Add email verification link instead of codes
   - Implement email change verification

### Code Quality
1. **Standardize Language**: Choose one language for comments and documentation
2. **Add Comprehensive Validation**: Implement all validations mentioned in README
3. **Error Handling**: Add proper exception handling and logging
4. **Code Organization**: Separate concerns better (e.g., services layer)

### Architecture Improvements
1. **Complete Feature Implementation**: Develop the placeholder apps
2. **API Documentation**: Add Swagger/OpenAPI documentation
3. **Testing**: Implement comprehensive test suite
4. **Database Migration**: Properly migrate legacy schema to Django-managed models

### Configuration
1. **Environment Variables**: Add validation and defaults for all required vars
2. **Docker Support**: Implement Docker for development and deployment
3. **CI/CD**: Add GitHub Actions for automated testing and deployment
4. **Monitoring**: Add logging and monitoring capabilities

### Performance & Scalability
1. **Caching Strategy**: Implement Redis caching for frequently accessed data
2. **Database Optimization**: Add indexes and optimize queries
3. **Async Processing**: Use Celery for email sending and background tasks
4. **API Optimization**: Implement pagination, filtering, and serialization optimization

### Development Practices
1. **Code Standards**: Add pre-commit hooks for code formatting (black, isort)
2. **Documentation**: Maintain up-to-date API and architecture docs
3. **Version Control**: Implement proper branching strategy (already mentioned in README)
4. **Code Review**: Establish code review processes