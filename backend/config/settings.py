import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Django requires a secret key; used internally for hashing
SECRET_KEY = 'local-network-key-no-internet-exposure'

DEBUG = True

# Allow access from any device on your local network
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',         # for viewing the database with easy ui based access
    'django.contrib.auth',          # needed?
    'django.contrib.contenttypes',  # Required for Django to work
    'django.contrib.sessions',      # needed?
    'django.contrib.messages',      #
    'django.contrib.staticfiles',   # For serving CSS/JS files
    'rest_framework',
    'corsheaders',
    'app.apps.SparcConfig',
    'channels',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Allow frontend to talk to backend
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',  # Basic HTTP handling
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Simple SQLite database (no PostgreSQL needed)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django',
        'USER': 'django',
        'PASSWORD': 'django',
        'HOST': 'db',  # This is the service name from docker-compose
        'PORT': '5432',  # Default PostgreSQL port
    }
}

# German language
LANGUAGE_CODE = 'en-uk'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework - simple configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # No authentication needed
    ],
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True  # Simple solution for local development
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF Configuration for cross-origin requests
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

os.makedirs(MEDIA_ROOT, exist_ok=True)

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}