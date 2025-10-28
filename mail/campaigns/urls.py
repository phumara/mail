from django.urls import path

from . import views

app_name = 'campaigns'

urlpatterns = [

    path('list/', views.campaign_list, name='campaign_list'),

    path('create/', views.campaign_create, name='campaign_create'),
    path('create-simple/', views.campaign_create_simple, name='campaign_create_simple'),

    path('<int:pk>/edit/', views.campaign_edit, name='campaign_edit'),

    path('<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
    path('<int:pk>/preview/', views.campaign_preview, name='campaign_preview'),
    path('<int:pk>/clone/', views.campaign_clone, name='campaign_clone'),
    path('<int:pk>/send/', views.campaign_send, name='campaign_send'),

    path('media/', views.MediaListView.as_view(), name='media_list'),
    path('media/upload/', views.MediaUploadView.as_view(), name='media_upload'),
    path('media/<int:pk>/delete/', views.MediaDeleteView.as_view(), name='media_delete'),

    # Analytics
    path('analytics/', views.campaign_analytics, name='campaign_analytics'),
    path('analytics/<int:campaign_id>/', views.campaign_analytics, name='campaign_analytics_detail'),

    # SMTP Management
    path('smtp-manager/', views.smtp_manager, name='smtp_manager'),
    path('smtp-manager/create/', views.smtp_provider_create, name='smtp_provider_create'),
    path('smtp-manager/<int:pk>/edit/', views.smtp_provider_edit, name='smtp_provider_edit'),
    path('smtp-manager/<int:pk>/delete/', views.smtp_provider_delete, name='smtp_provider_delete'),
    path('test-smtp-connection/<int:provider_id>/', views.test_smtp_connection, name='test_smtp_connection'),
    path('send-test-email/', views.send_test_email, name='send_test_email'),

    # Template Management
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('webhooks/handle/', views.webhook_handler, name='webhook_handler'),
]