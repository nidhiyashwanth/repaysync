# settings.py

from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-&8_d3fdx%^s3ox*e(y)j&xpf=u&5by@irhzh*wf4%7#vq96*%v')

# SECURITY WARNING: don't run with debug turned on in production!
# Ensure DEBUG is correctly set in your environment (e.g., .env file or system env vars)
# DEBUG = False for production, DEBUG = True for development
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Define allowed hosts for the BACKEND application
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'repaysync.codeindia.tech',
    'www.repaysync.codeindia.tech', # Added www variant
    '20.197.19.36', # Azure IP if needed directly
]

# CSRF settings: Trust origins from which secure requests (POST/PUT/DELETE with sessions/cookies) might come
# Primarily needed if using SessionAuthentication or forms, but good practice to include frontend origins.
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3001',          # Dev frontend
    'https://localhost:3001',         # Dev frontend (if using https locally)
    'http://127.0.0.1:8001',          # Built frontend served locally
    'https://127.0.0.1:8001',         # Built frontend served locally (https)
    'http://ui-repaysync.codeindia.tech', # Production frontend domain
    'https://ui-repaysync.codeindia.tech', # Production frontend domain (https)
    # Also include the backend's own origins if forms/sessions might originate there
    'http://repaysync.codeindia.tech',
    'https://repaysync.codeindia.tech',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_yasg',
    'corsheaders', # Ensure corsheaders is here
    'debug_toolbar',

    # Project apps
    'users',
    'customers',
    'interactions',
    'loans',
    'api',
    'core',
    'dummy_app',  # Added dummy app for testing dynamic permissions
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # CorsMiddleware should come BEFORE CommonMiddleware and other response-generating middleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware', # Debug toolbar usually last before closing body tag injection
]

ROOT_URLCONF = 'repaysync.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'repaysync.wsgi.application'


# Database
# ... (keep your existing database settings) ...
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=False) # Adjust ssl_require based on provider
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'repaysync'),
            'USER': os.environ.get('DB_USER', 'repaysync'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'repaysync098'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }


# Password validation
# ... (keep your existing AUTH_PASSWORD_VALIDATORS) ...
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
# ... (keep your existing I18N settings) ...
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# ... (keep your existing static/media settings) ...
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # Recommended for WhiteNoise

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User model
AUTH_USER_MODEL = 'users.User'

# REST Framework settings
# ... (keep your existing REST_FRAMEWORK settings) ...
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication', # Keep if you use Django admin or other session-based parts
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day', # Consider increasing if needed
    },
    'EXCEPTION_HANDLER': 'core.utils.custom_exception_handler',
}

# JWT settings
# ... (keep your existing SIMPLE_JWT settings) ...
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}


# Swagger settings
# ... (keep your existing SWAGGER_SETTINGS) ...
SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
   },
   'USE_SESSION_AUTH': False, # Set to False if primarily using JWT for API docs
}

# CORS settings - VERY IMPORTANT
# If DEBUG is True, all origins are allowed by default by CORS_ALLOW_ALL_ORIGINS=DEBUG
CORS_ALLOW_ALL_ORIGINS = DEBUG

# If DEBUG is False, ONLY these origins are allowed
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3001',          # Dev frontend
    'https://localhost:3001',         # Dev frontend (if using https locally)
    'http://127.0.0.1:8001',          # Built frontend served locally
    'https://127.0.0.1:8001',         # Built frontend served locally (https)
    'http://ui-repaysync.codeindia.tech', # Production frontend domain
    'https://ui-repaysync.codeindia.tech', # Production frontend domain (https)
]

# Allow credentials (cookies, authorization headers) to be sent with cross-origin requests
CORS_ALLOW_CREDENTIALS = True

# Optional: Define specific headers allowed, defaults are usually sufficient
# CORS_ALLOW_HEADERS = [ ... list headers ... ]
# Optional: Define specific methods allowed, defaults are usually sufficient
# CORS_ALLOW_METHODS = [ ... list methods ... ]


# Debug toolbar settings
# INTERNAL_IPS should list IPs from where YOU access the site for debugging
# It doesn't affect API access for frontend users.
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    # Add your development machine's IP if accessing remotely
    # Add the server IP if accessing the toolbar directly on the server
    '20.197.19.36',
]

# Logging configuration
# ... (keep your existing LOGGING settings) ...
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}', # Added process/thread
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO', # Set to DEBUG in development if needed
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler', # Use RotatingFileHandler
            'filename': os.path.join(BASE_DIR, 'logs/repaysync.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5, # Keep 5 backup logs
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'), # Control level via env var
            'propagate': True,
        },
        'repaysync': { # Your project's logger
            'handlers': ['console', 'file'],
            'level': 'INFO', # Set to DEBUG for more verbose app logging
            'propagate': False, # Don't propagate to root logger if handled here
        },
         'django.db.backends': { # Optional: Log SQL queries in DEBUG mode
            'level': 'DEBUG' if DEBUG else 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
    # Ensure logs directory exists
}
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)