import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Django requires a secret key; used internally for hashing
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me-in-production')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Add your Server IP and localhost
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost 127.0.0.1').split(' ')

INSTALLED_APPS = [
    #
    'daphne',
    # for viewing the database with easy ui based access
    'django.contrib.admin',
    #
    'django.contrib.auth',
    # Required for Django to work
    'django.contrib.contenttypes',
    #
    'django.contrib.sessions',
    #
    'django.contrib.messages',
    # For serving CSS/JS files
    'django.contrib.staticfiles',
    #
    'rest_framework',
    #
    'corsheaders',
    # used for real-time communication (WebSockets)
    'channels',
    #
    'app.apps.SparcConfig',
]

MIDDLEWARE = [
    # Allow frontend to talk to backend
    'corsheaders.middleware.CorsMiddleware',
    #
    'django.middleware.security.SecurityMiddleware',
    # Best practice for static files
    #'whitenoise.middleware.WhiteNoiseMiddleware',
    #
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Basic HTTP handling
    'django.middleware.common.CommonMiddleware',
    # CSRF protection
    'django.middleware.csrf.CsrfViewMiddleware',
    #
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #
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

#WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Simple SQLite database (no PostgreSQL needed)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'django'),
        'USER': os.environ.get('POSTGRES_USER', 'django'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'django'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': '5432',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

os.makedirs(MEDIA_ROOT, exist_ok=True)

#DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework - simple configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # No authentication needed
    ],
}

# CSRF / CORS Configuration
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000').split(' ')
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

# Django Channels Configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}
