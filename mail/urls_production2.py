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
    path('profile/password/', views.password_change, name='password_change'),
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
