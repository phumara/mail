from django.urls import path

from . import views

app_name = 'subscribers'

urlpatterns = [

    path('list/', views.subscriber_list, name='subscriber_list'),

    path('create/', views.subscriber_create, name='subscriber_create'),

    path('<int:pk>/edit/', views.subscriber_edit, name='subscriber_edit'),

    path('<int:pk>/delete/', views.subscriber_delete, name='subscriber_delete'),

    path('import/', views.subscriber_import, name='subscriber_import'),

    path('bounces/', views.subscriber_bounces, name='subscriber_bounces'),

    path('segments/', views.segment_list, name='segment_list'),

    path('segments/create/', views.segment_create, name='segment_create'),

    path('segments/<int:pk>/edit/', views.segment_edit, name='segment_edit'),

    path('segments/<int:pk>/delete/', views.segment_delete, name='segment_delete'),

    path('segments/<int:pk>/subscribers/', views.segment_subscribers, name='segment_subscribers'),
    path('search-subscribers/', views.search_subscribers, name='search_subscribers'),

]
