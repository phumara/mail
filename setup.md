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
---------------------------create .env file-----------------------

ALLOWED_HOSTS=localhost,127.0.0.1,phuma.ddns.net

# Database Configuration
#DATABASE_URL=postgresql://postgres:$ACARTelegramSupport7788#@localhost:5432/keymaster_db
DATABASE_URL=postgresql://postgres:%24ACARTelegramSupport7788%23@localhost:5432/mail_db
#DATABASE_URL=postgresql://Phum:Phumkey123@localhost:5432/keymaster_db
#DATABASE_URL=postgres://postgres:$ACARTelegramSupport7788#@127.0.0.1:5432/keymaster_db
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@keymaster.com

# Security Settings
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7

# File Upload Settings
MAX_UPLOAD_SIZE=5242880

# Pagination
PAGE_SIZE=20




3.create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt



## 📋 Overview

This configuration will deploy your Django mail application at `phuma.ddns.net/mail/` alongside your existing keymasters application at `phuma.ddns.net/mail/` with complete isolation between the two applications.

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

**File: `mail/settings_productions.py`** - Add these modifications:

```python
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


---
urls_production.py
----------------------------------------------------
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import redirect
from . import views

def api_home(request):
    return JsonResponse({
        "name": "Mail Campaign API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "mail/admin/",
            "accounts": {
                "login": "mail/accounts/login/",
                "logout": "mail/accounts/logout/",
                "profile": "mail/accounts/profile/",
            },
            "campaigns": "mail/campaigns/",
            "subscribers": "mail/subscribers/",
        },
        "status": "Production"
    }, json_dumps_params={'indent': 2})


# All mail routes grouped here
mail_urlpatterns = [
    path('', views.home, name='home'),

    # Admin
    path('admin/', admin.site.urls),

    # Auth
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('accounts/password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # Accounts
    path('accounts/', include('accounts.urls')),

    # Campaigns
    path('campaigns/', include('campaigns.urls')),

    # Subscribers
    path('subscribers/', include('subscribers.urls')),

    # API
    path('api/', api_home, name='api_home'),
]


# Mount everything under /mail/
urlpatterns = [
    path('', lambda request: redirect('/mail/')),  # Redirect root to /mail/
    path('mail/', include(mail_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


---

## 🔧 **Step 3: Gunicorn Socket Configuration**

Replace with isolated gunicorn socket for mail app:

**File: `/etc/systemd/system/gunicorn_mail.socket`**

```ini
[Unit]
Description=gunicorn socket mail

[Socket]
ListenStream=/run/gunicorn_mail.sock
SocketUser=www-data
SocketMode=0660

[Install]
WantedBy=sockets.target
```

---

## 🔧 **Step 4: Systemd Service Configuration**

**File: `/etc/systemd/system/gunicorn_mail.service`**

```ini
[Unit]
Description=gunicorn daemon mail
Requires=gunicorn_mail.socket
After=network.target

[Service]
#Type=forking
PIDFile=/run/gunicorn_mail/pid
User=root
Group=root
RuntimeDirectory=gunicorn_mail
WorkingDirectory=/root/web/mail
Environment=PATH=/root/web/mail/venv/bin
Environment="DJANGO_SETTINGS_MODULE=mail.settings_production"
ExecStart=/root/web/mail/venv/bin/gunicorn \
          --pid /run/gunicorn_mail/pid \
          --bind unix:/run/gunicorn_mail.sock \
          --workers 3 \
          mail.wsgi:application
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
    # mail App (Django/Gunicorn)
    # -------------------------------
    include snippets/mail.conf;

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

xxxx**File: `/etc/nginx/snippets/mail.conf`** (mail app)
```nginx(mail.conf)

# Static files for mail app
location /mail/mail/static/ {
    alias /root/web/mail/mail/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, no-transform";
    access_log off;
    add_header Access-Control-Allow-Origin *;
    try_files $uri $uri/ =404;
}

# Media files for mail app
location /mail/mail/edia/ {
    alias /root/web/mail/mail/media/;
    expires 30d;
    add_header Cache-Control "public, no-transform";
    access_log off;
    try_files $uri $uri/ =404;
}

# Main Money app backend
location /mail/ {
    proxy_pass http://unix:/run/gunicorn_mail.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_redirect off;
}

# Redirect /mail → /mail/
location = /mail {
    return 301 https://$host/mail/;
}
# Redirect root to /mail/
  #  location = / {
 #       return 301 https://$host/mail/;
#    }
---

## 📋 **Step 8: Manual Deployment Steps**

---

## 🔍 **Step 9: Verification & Testing**

### **Service Status Checks**
```bash
# Check money app service
systemctl status gunicorn_mail.service gunicorn_mail.socket

# Check nginx
systemctl status nginx

# Check logs
tail -f /root/web/money/logs/gunicorn-access.log
tail -f /root/web/money/logs/gunicorn-error.log
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```


---

## 🛠️ **Step 10: Maintenance Commands**

### **Update mail App**
```bash
cd /root/web/mail
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
systemctl restart gunicorn_mail.service

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
cd /root/web/mail
source venv/bin/activate

# Create backup
cp db.sqlite3 backups/money_db_$(date +%Y%m%d).sqlite3

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

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