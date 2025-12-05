"""
URLs para el core (dashboard)
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]
