import os
from pathlib import Path

# Load environment variables
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# CORE SETTINGS
# =============================================================================

# Secret key for cryptographic signing
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')

# Debug mode - shows detailed error pages (ONLY for development)
DEBUG = config('DEBUG', default=True, cast=bool)

# Hosts that are allowed to serve this Django site
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0').split(',')

# =============================================================================
# INSTALLED APPS
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',        # Admin interface
    'django.contrib.auth',         # User authentication
    'django.contrib.contenttypes', # Content type framework
    'django.contrib.sessions',     # Session framework
    'django.contrib.messages',     # Messaging framework
    'django.contrib.staticfiles',  # Static file handling
    'posts',                       # Your posts app
    'rest_framework',              # Django REST framework
    'api',                         # Your API app
]

# =============================================================================
# MIDDLEWARE - Order matters!
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',# Security headers
    'django.contrib.sessions.middleware.SessionMiddleware', # Session handling
    'django.middleware.common.CommonMiddleware',            # Common functionality
    'django.middleware.csrf.CsrfViewMiddleware',           # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # User auth
    'django.contrib.messages.middleware.MessageMiddleware',    # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
]

ROOT_URLCONF = 'noteApp.urls'

# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Your template directory
        'APP_DIRS': True,                  # Look for templates in app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',    # Debug info in templates
                'django.template.context_processors.request',  # Request object in templates
                'django.contrib.auth.context_processors.auth', # User info in templates
                'django.contrib.messages.context_processors.messages', # Messages in templates
            ],
        },
    },
]

WSGI_APPLICATION = 'noteApp.wsgi.application'

# =============================================================================
# DATABASE
# =============================================================================

# SQLite database for development (simple file-based database)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        # Prevents passwords similar to user info
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8,}  # Minimum 8 characters
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        # Prevents common passwords like "password123"
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        # Prevents purely numeric passwords
    },
]

# =============================================================================
# REST FRAMEWORK (API SETTINGS)
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication', # Use Django sessions for API
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', # Require login for API access
    ],
}

# =============================================================================
# SECURITY SETTINGS - DOCKER/DEVELOPMENT FRIENDLY
# =============================================================================

# CSRF Protection - prevents cross-site request forgery
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',   # Docker container
    'http://127.0.0.1:8080',  # Docker container
    'http://0.0.0.0:8080',    # Docker container
    'http://localhost:8000',  # Local development
    'http://127.0.0.1:8000',  # Local development
]

# Cookie Settings for Development (less strict for Docker)
CSRF_COOKIE_SECURE = False      # Only send CSRF cookie over HTTPS (False for development)
SESSION_COOKIE_SECURE = False   # Only send session cookie over HTTPS (False for development)
CSRF_COOKIE_HTTPONLY = False    # Allow JavaScript access to CSRF token (needed for AJAX)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie (security)

# Cookie Domain Settings
CSRF_COOKIE_DOMAIN = None    # Use default domain
SESSION_COOKIE_DOMAIN = None # Use default domain

# Basic Security Headers
SECURE_BROWSER_XSS_FILTER = True    # Enable XSS filtering in browsers
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'            # Prevent page from being embedded in frames

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'  # Default language
TIME_ZONE = 'UTC'        # Default timezone
USE_I18N = True          # Enable internationalization
USE_TZ = True            # Use timezone-aware datetimes

# =============================================================================
# STATIC & MEDIA FILES
# =============================================================================

# Replace the problematic section with:
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Different directory

# Media files (user uploads)
MEDIA_URL = '/media/'                      # URL prefix for media files
MEDIA_ROOT = BASE_DIR / 'media'           # Where uploaded files are stored

# =============================================================================
# AUTHENTICATION URLS
# =============================================================================

# =============================================================================
# SECURITY SETTINGS - DOCKER/DEVELOPMENT FRIENDLY
# =============================================================================

# CSRF Protection - prevents cross-site request forgery
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',   # Docker container
    'http://127.0.0.1:8080',  # Docker container
    'http://0.0.0.0:8080',    # Docker container
    'http://localhost:8000',  # Local development
    'http://127.0.0.1:8000',  # Local development
]

# Cookie Settings for Development (less strict for Docker)
CSRF_COOKIE_SECURE = False      # Only send CSRF cookie over HTTPS (False for development)
SESSION_COOKIE_SECURE = False   # Only send session cookie over HTTPS (False for development)
CSRF_COOKIE_HTTPONLY = False    # Allow JavaScript access to CSRF token (needed for AJAX)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie (security)

# Cookie Domain Settings
CSRF_COOKIE_DOMAIN = None    # Use default domain
SESSION_COOKIE_DOMAIN = None # Use default domain

# Basic Security Headers
SECURE_BROWSER_XSS_FILTER = True    # Enable XSS filtering in browsers
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'            # Prevent page from being embedded in frames

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'  # Default language
TIME_ZONE = 'UTC'        # Default timezone
USE_I18N = True          # Enable internationalization
USE_TZ = True            # Use timezone-aware datetimes

# =============================================================================
# STATIC & MEDIA FILES
# =============================================================================


LOGIN_URL = '/accounts/login/'      # Where to redirect if login required
LOGIN_REDIRECT_URL = '/posts/'      # Where to go after successful login
LOGOUT_REDIRECT_URL = '/'           # Where to go after logout

# =============================================================================
# FILE UPLOAD LIMITS
# =============================================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB - max file size in memory
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB - max request size

# Custom app limits
MAX_TITLE_LENGTH = 200              # Maximum post title length
MAX_CONTENT_LENGTH = 10000          # Maximum post content length
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB - max upload size

# =============================================================================
# DJANGO DEFAULTS
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Default primary key type
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'