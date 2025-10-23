from django.urls import path

from . import views

urlpatterns = [

    path('list/', views.campaign_list, name='campaign_list'),

    path('create/', views.campaign_create, name='campaign_create'),
    path('create-simple/', views.campaign_create_simple, name='campaign_create_simple'),

    path('<int:pk>/edit/', views.campaign_edit, name='campaign_edit'),

    path('<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),

    path('media/', views.media_list, name='media_list'),

    path('templates/', views.template_list, name='template_list'),

    path('templates/create/', views.template_create, name='template_create'),

    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),

    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),

    path('analytics/', views.campaign_analytics, name='campaign_analytics'),

]