"""
Configuración del admin para la app de accounts
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administración personalizada para el modelo User
    """
    list_display = [
        'username', 'employee_id', 'get_full_name', 'email',
        'role_badge', 'department', 'is_active_employee', 'is_staff'
    ]
    list_filter = [
        'role', 'department', 'is_active', 'is_staff',
        'is_active_employee', 'date_joined'
    ]
    search_fields = [
        'username', 'first_name', 'last_name', 'email',
        'employee_id', 'department', 'position'
    ]
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información de Empleado', {
            'fields': ('employee_id', 'role', 'department', 'position',
                      'phone_number', 'photo')
        }),
        ('Información Personal', {
            'fields': ('birth_date', 'hire_date', 'address',
                      'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Estado', {
            'fields': ('is_active_employee',)
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('employee_id', 'role', 'email', 'first_name', 'last_name')
        }),
    )

    def role_badge(self, obj):
        """Muestra el rol con color"""
        color = obj.get_role_display_color()
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Rol'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Administración para el perfil de usuario
    """
    list_display = [
        'user', 'education_level', 'theme_preference',
        'email_notifications', 'updated_at'
    ]
    list_filter = ['theme_preference', 'language_preference', 'email_notifications']
    search_fields = ['user__username', 'user__email', 'professional_license']
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip', 'failed_login_attempts']

    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información Profesional', {
            'fields': ('professional_license', 'education_level',
                      'specializations', 'certifications')
        }),
        ('Seguridad', {
            'fields': ('last_login_ip', 'failed_login_attempts', 'account_locked_until')
        }),
        ('Preferencias', {
            'fields': ('theme_preference', 'language_preference', 'email_notifications')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Administración para el log de auditoría
    """
    list_display = [
        'timestamp', 'user', 'action', 'model_name',
        'object_id', 'ip_address'
    ]
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = [
        'user__username', 'model_name', 'object_id',
        'description', 'ip_address'
    ]
    readonly_fields = [
        'user', 'action', 'model_name', 'object_id',
        'description', 'ip_address', 'user_agent', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        """No permitir agregar logs manualmente"""
        return False

    def has_change_permission(self, request, obj=None):
        """No permitir editar logs"""
        return False
