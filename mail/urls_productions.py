from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from . import views

def api_home(request):
    return JsonResponse({
        "name": "Mail Campaign API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "admin/",
            "accounts": {
                "login": "accounts/login/",
                "logout": "accounts/logout/",
                "profile": "accounts/profile/",
            },
            "campaigns": "campaigns/",
            "subscribers": "subscribers/",
        },
        "status": "Production"
    }, json_dumps_params={'indent': 2})


urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", views.custom_logout, name="logout"),
    path("accounts/password-change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path("accounts/password-change/done/", auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("accounts/", include("accounts.urls")),
    path("subscribers/", include("subscribers.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("api/", api_home, name="api_home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)