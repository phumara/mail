from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

production_urlpatterns = [
    path('admin/', admin.site.urls),
    path('campaigns/', include('campaigns.urls')),
    path('subscribers/', include('subscribers.urls')),
    path('', include('campaigns.urls')),  # Default to campaigns app
]

urlpatterns = [
    path('mail/', include(production_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)