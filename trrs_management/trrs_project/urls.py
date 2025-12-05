"""
URL configuration for TR&RS Management System
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="TR&RS Management API",
        default_version='v1',
        description="API del Sistema de Gestión Integral TR&RS",
        terms_of_service="https://www.trrs.com/terms/",
        contact=openapi.Contact(email="contacto@trrs.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Apps URLs
    path('', include('trrs_project.apps.core.urls', namespace='core')),
    path('accounts/', include('trrs_project.apps.accounts.urls', namespace='accounts')),
    path('dashboard/', include('trrs_project.apps.core.urls', namespace='dashboard')),
    path('operations/', include('trrs_project.apps.operations.urls', namespace='operations')),
    path('maintenance/', include('trrs_project.apps.maintenance.urls', namespace='maintenance')),
    path('hseq/', include('trrs_project.apps.hseq.urls', namespace='hseq')),
    path('purchases/', include('trrs_project.apps.purchases.urls', namespace='purchases')),
    path('hr/', include('trrs_project.apps.hr.urls', namespace='hr')),
    path('reports/', include('trrs_project.apps.reports.urls', namespace='reports')),

    # API URLs
    path('api/v1/', include('trrs_project.apps.operations.api.urls')),
    path('api/v1/', include('trrs_project.apps.maintenance.api.urls')),
    path('api/v1/', include('trrs_project.apps.hseq.api.urls')),

    # API Authentication
    path('api-auth/', include('rest_framework.urls')),

    # Swagger/OpenAPI Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Notifications
    path('notifications/', include('notifications.urls', namespace='notifications')),
]

# Configuración personalizada del admin
admin.site.site_header = "TR&RS Management System"
admin.site.site_title = "TR&RS Admin"
admin.site.index_title = "Panel de Administración"

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar (solo en desarrollo)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
