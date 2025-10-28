# 🚀 Final Django Mail App Multi-App Deployment Configuration   
## 🛠️ Technology 
1.Django 
2.Nginx (snippet like lego,nignx path)
3.Gunicorn (different)
4.Postgresql (database) mail_db;

## Database configuration
1. Database: mail_db;
sudo -u postgres psql
CREATE DATABASE mail_db;
CREATE USER mail_user WITH PASSWORD 'YourSecurePassword';
GRANT ALL PRIVILEGES ON DATABASE mail_db TO mail_user;
\q  
2. Update your .env file with the database URL:
DATABASE_URL=postgres://mail_user:YourSecurePassword@localhost:5432/mail_db

3.create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt



## 📋 Overview

This configuration will deploy your Django Money application at `phuma.ddns.net/money/` alongside your existing keymasters application at `phuma.ddns.net/keymasters/` with complete isolation between the two applications.

### ✅ **Final URLs After Deployment**
- **Keymasters**: `https://phuma.ddns.net/keymasters/` (unchanged, existing app)
- **Money App**: `https://phuma.ddns.net/money/` (new deployment)
- **Money Admin**: `https://phuma.ddns.net/money/admin/`

## 🎯 **Key Features**
- ✅ **Complete Isolation**: Separate services, configs, and static files
- ✅ **Zero Downtime**: Existing keymasters app remains untouched
- ✅ **Independent Management**: Each app can be updated/restarted separately
- ✅ **Shared SSL**: Uses existing SSL certificate for the domain

---

## 🔧 **Step 1: Prepare Django Settings** 

Update your Django settings for multi-app deployment:

**File: `config/settings_productions.py`** - Add these modifications:

```python
from .settings import *
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set in .env or environment!")

# Production settings
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

# Allowed hosts from environment variable
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
# Database configuration using DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Allowed hosts for production
#ALLOWED_HOSTS = ['phuma.ddns.net', 'localhost', '127.0.0.1']

# nginx handles the /money/ prefix stripping, so Django works with clean URLs
#FORCE_SCRIPT_NAME = '/money/'

# Use production URL configuration
ROOT_URLCONF = 'config.urls_production'

# Static and media URLs (nginx strips /money/ prefix, so Django sees clean URLs)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Production paths for static and media files
STATIC_ROOT = '/root/web/money/staticfiles/'
MEDIA_ROOT = '/root/web/money/media/'

# Static files directories
STATICFILES_DIRS = ['/root/web/money/static'] if os.path.exists('/root/web/money/static') else []

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
SESSION_COOKIE_NAME = 'money_sessionid'
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# CSRF Configuration
CSRF_COOKIE_NAME = 'money_csrftoken'
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Must be False for CSRF to work properly
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF
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
LOGIN_URL = '/money/accounts/login/'
LOGIN_REDIRECT_URL = '/money/'
LOGOUT_REDIRECT_URL = '/money/accounts/login/'

# Override base settings to ensure consistency
LOGIN_URL = '/money/accounts/login/'
LOGIN_REDIRECT_URL = '/money/'
LOGOUT_REDIRECT_URL = '/money/accounts/login/'

# Session engine and backend (duplicate - removing)
# SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database-backed sessions
# SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Cache configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'production-cache',
        'TIMEOUT': 3600,
        'OPTIONS': {'MAX_ENTRIES': 1000},
    }
}

# Create necessary directories
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
os.makedirs(BASE_DIR / 'data', exist_ok=True)


---
urls_production.py
----------------------------------------------------
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import redirect
from finance import views
from django.contrib.auth import views as auth_views

def api_home(request):
    return JsonResponse({
        "name": "Money Finance API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "money/admin/",
            "auth": {
                "login": "money/accounts/login/",
                "logout": "money/accounts/logout/",
                "register": "money/register/",
            },
            "finance": "money/transactions/",
        },
        "status": "Production"
    }, json_dumps_params={'indent': 2})


# All finance routes grouped here
money_urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Admin
    path('admin/', admin.site.urls),

    # Auth
    path('register/', views.register, name='register'),
    path('accounts/login/', views.custom_login, name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),

    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.budget_add, name='budget_add'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),

    # API
    path('api/', include('finance.api_urls')),

    # Exchange rates
    path('exchange-rates/', views.exchange_rate_status, name='exchange_rate_status'),
    path('api/exchange-rates/status/', views.exchange_rate_status_api, name='exchange_rate_status_api'),
    path('exchange-rates/update/', views.manual_update_exchange_rates, name='update_exchange_rates'),

    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Debug
    path('debug/csrf/', views.csrf_debug, name='csrf_debug'),
    path('debug/auth/', views.auth_debug, name='auth_debug'),
    path('debug/login/', views.login_debug, name='login_debug'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]


# Mount everything under /money/
urlpatterns = [
    path('', lambda request: redirect('/money/')),  # Redirect root to /money/
    path('money/', include(money_urlpatterns)),
    #path('money/api/', api_home, name='api_home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)




-------------------------------------------------------


## 🔧 **Step 2: Environment Configuration**

Create environment file for production:

**File: `/root/web/money/.env`**

```bash
# Django Production Configuration
DEBUG=False
SECRET_KEY=your-very-long-and-secure-secret-key-here  # Change this to a secure random string
ALLOWED_HOSTS=phuma.ddns.net,www.phuma.ddns.net

# Database Configuration
# Make sure to URL encode special characters in passwords
DATABASE_URL=postgresql://postgres:%24ACARTelegramSupport7788%23@localhost:5432/money_db

# Email Configuration (Update with your email service provider details)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com  # or your email provider's SMTP server
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@phuma.ddns.net

# Security Settings
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https

# Static and Media files
STATIC_URL=/money/static/
STATIC_ROOT=/root/web/money/staticfiles
MEDIA_URL=/money/media/
MEDIA_ROOT=/root/web/money/media

# Cache settings (if you're using Redis or Memcached)
# CACHE_URL=redis://127.0.0.1:6379/1

# Celery settings (if you're using Celery)
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_DIR=/root/web/money/logs

# Application specific settings
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes
PAGE_SIZE=20

# JWT Settings (if you're using JWT authentication)
JWT_SECRET_KEY=your-secure-jwt-secret-key-here  # Change this
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Rate limiting
API_RATE_LIMIT=100/hour  # Adjust based on your needs

# CORS Settings
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://phuma.ddns.net,https://www.phuma.ddns.net

```

---

## 🔧 **Step 3: Gunicorn Socket Configuration**

Create isolated gunicorn socket for money app:

**File: `/etc/systemd/system/gunicorn_money.socket`**

```ini
[Unit]
Description=gunicorn socket money

[Socket]
ListenStream=/run/gunicorn_money.sock
SocketUser=www-data
SocketMode=0660

[Install]
WantedBy=sockets.target
```

---

## 🔧 **Step 4: Systemd Service Configuration**

**File: `/etc/systemd/system/gunicorn_money.service`**

```ini
[Unit]
Description=gunicorn daemon money
Requires=gunicorn_money.socket
After=network.target

[Service]
#Type=forking
PIDFile=/run/gunicorn_money/pid
User=root
Group=root
RuntimeDirectory=gunicorn_money
WorkingDirectory=/root/web/money
Environment=PATH=/root/web/money/venv/bin
Environment="DJANGO_SETTINGS_MODULE=config.settings_production"
ExecStart=/root/web/money/venv/bin/gunicorn \
          --pid /run/gunicorn_money/pid \
          --bind unix:/run/gunicorn_money.sock \
          --workers 3 \
          config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

---

## 🔧 **Step 5: Nginx Configuration**

**File: `/etc/nginx/sites-available/phuma`** (replace your default config)

```nginx
# Redirect all HTTP to HTTPS
server {
    listen 80;
    server_name phuma.ddns.net;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name phuma.ddns.net;

    # SSL configuration (Let’s Encrypt)
    ssl_certificate /etc/letsencrypt/live/phuma.ddns.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/phuma.ddns.net/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # -------------------------------
    # Keymasters App (Django/Gunicorn)
    # -------------------------------
    include snippets/keymasters.conf;

    # -------------------------------
    # Money App (new one you asked)
    # -------------------------------
    include snippets/money.conf;

    # -------------------------------
    # Redirects
    # -------------------------------
    # Redirect root → /keymasters/
    #location = / {
       # return 301 https://$host/keymasters/;
   #}
location / {
    root /var/www/phum;
    index index.html;
    try_files $uri $uri/ /index.html;
}
}

xxxx**File: `/etc/nginx/snippets/money.conf`** (money app)
```nginx(money.conf)

# Static files for Money app
location /money/static/ {
    alias /root/web/money/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, no-transform";
    access_log off;
    add_header Access-Control-Allow-Origin *;
    try_files $uri $uri/ =404;
}

# Media files for Money app
location /money/media/ {
    alias /root/web/money/media/;
    expires 30d;
    add_header Cache-Control "public, no-transform";
    access_log off;
    try_files $uri $uri/ =404;
}

# Main Money app backend
location /money/ {
    proxy_pass http://unix:/run/gunicorn_money.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_redirect off;
}

# Redirect /money → /money/
location = /money {
    return 301 https://$host/money/;
}
# Redirect root to /money/
  #  location = / {
 #       return 301 https://$host/money/;
#    }
---
xxxx.nginx for keymasters app /etc/nginx/snippets/keymasters.conf ()
-----------------------------------------------------------------------
# Serve static files for /keymasters/static/
location /keymasters/static/ {
    alias /root/web/keymasters/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, no-transform";
    access_log off;
    add_header Access-Control-Allow-Origin *;
    try_files $uri $uri/ =404;
}

# Also handle direct /static/ requests (in case Django generates these)
    location /static/ {
        alias /root/web/keymasters/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        access_log off;
        try_files $uri $uri/ =404;
    }
# Serve media files for /keymasters/media/
location /keymasters/media/ {
    alias /root/web/keymasters/media/;
    expires 30d;
    add_header Cache-Control "public, no-transform";
    access_log off;
    try_files $uri $uri/ =404;
}

# Also handle direct /media/ requests
    location /media/ {
        alias /root/web/keymasters/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        access_log off;
        try_files $uri $uri/ =404;
    }
# Favicon
location = /keymasters/favicon.ico {
    alias /root/web/keymasters/staticfiles/favicon.ico;
    expires 30d;
    access_log off;
    log_not_found off;
}

# Main app via Gunicorn socket
location /keymasters/ {
    proxy_pass http://unix:/run/gunicorn.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_redirect off;
}

# Redirect /keymasters → /keymasters/
location = /keymasters {
    return 301 https://$host/keymasters/;
}

----------------------------------------------------------------------------

## 📋 **Step 8: Manual Deployment Steps**

---

## 🔍 **Step 9: Verification & Testing**

### **Service Status Checks**
```bash
# Check money app service
systemctl status gunicorn_money.service gunicorn_money.socket

# Check nginx
systemctl status nginx

# Check logs
tail -f /root/web/money/logs/gunicorn-access.log
tail -f /root/web/money/logs/gunicorn-error.log
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### **URL Testing**
- ✅ **Keymasters**: `https://phuma.ddns.net/keymasters/`
- ✅ **Money App**: `https://phuma.ddns.net/money/`
- ✅ **Money Admin**: `https://phuma.ddns.net/money/admin/`
- ✅ **Static Files**: `https://phuma.ddns.net/money/static/`

---

## 🛠️ **Step 10: Maintenance Commands**

### **Update Money App**
```bash
cd /root/web/money
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
systemctl restart gunicorn_money.service
```

### **Restart Services**
```bash
# Restart money app only
systemctl restart gunicorn_money.service

# Restart both apps
systemctl restart nginx

# Restart keymasters (if needed)
systemctl restart gunicorn  # Your existing service name
```

### **View Logs**
```bash
# Money app logs
tail -f /root/web/money/logs/gunicorn-access.log
tail -f /root/web/money/logs/gunicorn-error.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### **Database Management** change to postgresql
```bash
cd /root/web/money
source venv/bin/activate

# Create backup
cp db.sqlite3 backups/money_db_$(date +%Y%m%d).sqlite3

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

## 🔒 **Security Features**

- ✅ **SSL/TLS**: Uses existing Let's Encrypt certificate
- ✅ **Isolated Services**: Separate systemd services and sockets
- ✅ **Security Headers**: X-Frame-Options, XSS Protection, etc.
- ✅ **File Permissions**: Proper ownership and access controls
- ✅ **Process Isolation**: Different Unix sockets for each app

---

## 🎯 **Final Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                     │
│                   (Port 443 - HTTPS)                       │
└─────┬─────────────────────────────────────┬─────────────────┘
      │                                     │
      ▼                                     ▼
┌─────────────────┐                 ┌─────────────────┐
│ /keymasters/*   │                 │ /money/*        │
│                 │                 │                 │
│ gunicorn.sock   │                 │ money.sock      │
│ (existing)      │                 │ (new)           │
└─────────────────┘                 └─────────────────┘
      │                                     │
      ▼                                     ▼
┌─────────────────┐                 ┌─────────────────┐
│ Keymasters App  │                 │ Money App       │
│ Django Project  │                 │ Django Project  │
│ (unchanged)     │                 │ (new)           │
└─────────────────┘                 └─────────────────┘
```

## ✅ **Deployment Checklist**

- [ ] **Code uploaded** to `/root/web/money/`
- [ ] **Virtual environment** created and dependencies installed
- [ ] **Database migrations** applied
- [ ] **Static files** collected
- [ ] **Environment file** configured
- [ ] **Systemd services** created and enabled
- [ ] **Nginx configuration** updated
- [ ] **Services started** and verified
- [ ] **SSL certificate** working
- [ ] **Both apps tested** and accessible
- [ ] **Superuser created** for money app
- [ ] **Logs verified** - no errors

---

## 🎉 **Success!**

Your Django Money application is now successfully deployed at `https://phuma.ddns.net/money/` alongside your existing keymasters application with complete isolation and zero conflicts!

**Final URLs:**
- 🔷 **Keymasters**: `https://phuma.ddns.net/keymasters/`
- 🔷 **Money App**: `https://phuma.ddns.net/money/`
- 🔷 **Money Admin**: `https://phuma.ddns.net/money/admin/`

(What we meet and difficult)
1.
Database create supperuser for production
python manage.py createsuperuser --settings=config.settings_production

2.Session path 
  we use .env show we use secret_key from it.
  
  ''''
  from dotenv import load_dotenv

  load_dotenv()

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set in .env or environment!")

    # Production settings
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
SESSION_COOKIE_PATH = '/'
CSRF_COOKIE_PATH = '/'

'''''

3.nginx path
    we don't know how we use the same domain with nginx path by use snippets and include  it .
    we use prefix (urls_production)

    # Mount everything under /money/
urlpatterns = [
    path('', lambda request: redirect('/money/')),  # Redirect root to /money/
    path('money/', include(money_urlpatterns)),
    #path('money/api/', api_home, name='api_home'),
]

4.Database move to Postgresql and connect with .env
   
    # Database configuration using DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

5.create virtual venv (ubuntu)
    python3 -m venv venv

6.check error 
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart gunicorn_money

7.
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u gunicorn_money -f
tail -f /root/web/money/logs/gunicorn.log