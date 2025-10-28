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