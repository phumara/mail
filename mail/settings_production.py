from .settings import *
from decouple import config
import os
import dj_database_url

SECRET_KEY = config('SECRET_KEY')

# Production settings
DEBUG = config("DEBUG", default=False, cast=bool)

# Allowed hosts from environment variable
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# Database configuration using DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}



# Allowed hosts for production

#ALLOWED_HOSTS = ['phuma.ddns.net', 'localhost', '127.0.0.1']



# nginx handles the /money/ prefix stripping, so Django works with clean URLs

#FORCE_SCRIPT_NAME = '/money/'



# Use production URL configuration

ROOT_URLCONF = 'mail.urls_productions'



# Static and media URLs
STATIC_URL = '/static/'
MEDIA_URL = '/media/'



# Production paths for static and media files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



# Static files directories
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]



# # Database configuration

# DATABASES = {

#     'default': {

#         'ENGINE': 'django.db.backends.sqlite3',

#         'NAME': BASE_DIR / 'db.sqlite3',

#     }

# }



# Force script name for proper URL handling

#FORCE_SCRIPT_NAME = '/money'



# Session Configuration

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_NAME = 'mail_sessionid'

SESSION_COOKIE_DOMAIN = None

SESSION_COOKIE_PATH = '/'

SESSION_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_AGE = 86400  # 24 hours

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_SAVE_EVERY_REQUEST = True



# CSRF Configuration

CSRF_COOKIE_NAME = 'mail_csrftoken'

CSRF_COOKIE_DOMAIN = None

CSRF_COOKIE_PATH = '/'

CSRF_COOKIE_SECURE = True

CSRF_COOKIE_HTTPONLY = False  # Must be False for CSRF to work properly

CSRF_COOKIE_SAMESITE = 'Lax'

#CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF

CSRF_TRUSTED_ORIGINS = [

    'https://phuma.ddns.net',

    'https://www.phuma.ddns.net',

]

CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'



# Additional CSRF settings for proxy setup

CSRF_COOKIE_AGE = None  # Session-based CSRF cookie

CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'



# Security settings for production

SECURE_SSL_REDIRECT = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



# Enhanced security settings

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_PRELOAD = True

# CORS settings for production

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [

    "https://phuma.ddns.net",

]



# Session configuration for production (duplicate - removing)

# SESSION_COOKIE_AGE = 86400  # 24 hours

# SESSION_SAVE_EVERY_REQUEST = True

# SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Content security

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

X_FRAME_OPTIONS = 'DENY'







# CSRF trusted origins for production

# (Already defined above in CSRF Configuration section)



# Proxy settings for nginx

USE_X_FORWARDED_HOST = True

USE_X_FORWARDED_PORT = True



# Authentication URLs (keep /money/ prefix for correct redirection)

LOGIN_URL = '/accounts/login/'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/accounts/login/'



# Override base settings to ensure consistency
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'



# Session engine and backend
# SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database-backed sessions
# SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'



# Cache configuration for production
# For a more scalable solution in a multi-process or multi-server environment, consider using Redis.
CACHES = {

    'default': {

        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',

        'LOCATION': 'production-cache',

        'TIMEOUT': 3600,

        'OPTIONS': {'MAX_ENTRIES': 1000},

    }

}



# Override authentication URLs for production with /mail/ prefix
LOGIN_URL = '/mail/accounts/login/'
LOGIN_REDIRECT_URL = '/mail/'
LOGOUT_REDIRECT_URL = '/mail/accounts/login/'

# Create necessary directories
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'media'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'staticfiles'), exist_ok=True)