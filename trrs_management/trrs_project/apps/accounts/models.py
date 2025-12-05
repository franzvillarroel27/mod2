"""
Modelos para el sistema de autenticación y gestión de usuarios
"""

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Modelo de usuario personalizado con campos adicionales
    """

    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('gerente_operaciones', 'Gerente de Operaciones'),
        ('supervisor_mantenimiento', 'Supervisor de Mantenimiento'),
        ('coordinador_hseq', 'Coordinador HSEQ'),
        ('comprador', 'Comprador'),
        ('tecnico_operador', 'Técnico/Operador'),
        ('visitante', 'Visitante'),
    ]

    # Campos adicionales
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='visitante',
        verbose_name='Rol'
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Código de Empleado'
    )
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    photo = models.ImageField(
        upload_to='users/photos/',
        blank=True,
        null=True,
        verbose_name='Foto de Perfil'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Departamento'
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Cargo'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Nacimiento'
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Contratación'
    )
    is_active_employee = models.BooleanField(
        default=True,
        verbose_name='Empleado Activo'
    )
    address = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Contacto de Emergencia'
    )
    emergency_contact_phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name='Teléfono de Emergencia'
    )

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']
        permissions = [
            ('view_all_users', 'Puede ver todos los usuarios'),
            ('manage_roles', 'Puede gestionar roles de usuarios'),
            ('export_users', 'Puede exportar datos de usuarios'),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})" if self.employee_id else self.username

    def get_role_display_color(self):
        """Retorna un color basado en el rol para la UI"""
        colors = {
            'admin': 'danger',
            'gerente_operaciones': 'primary',
            'supervisor_mantenimiento': 'info',
            'coordinador_hseq': 'warning',
            'comprador': 'success',
            'tecnico_operador': 'secondary',
            'visitante': 'light',
        }
        return colors.get(self.role, 'secondary')

    def has_role(self, role):
        """Verifica si el usuario tiene un rol específico"""
        return self.role == role

    def can_manage_operations(self):
        """Verifica si puede gestionar operaciones"""
        return self.role in ['admin', 'gerente_operaciones']

    def can_manage_maintenance(self):
        """Verifica si puede gestionar mantenimiento"""
        return self.role in ['admin', 'supervisor_mantenimiento', 'gerente_operaciones']

    def can_manage_hseq(self):
        """Verifica si puede gestionar HSEQ"""
        return self.role in ['admin', 'coordinador_hseq']


class UserProfile(models.Model):
    """
    Perfil extendido del usuario con información adicional
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario'
    )

    # Información profesional
    professional_license = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Licencia Profesional'
    )
    education_level = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nivel de Educación'
    )
    specializations = models.TextField(
        blank=True,
        verbose_name='Especializaciones'
    )
    certifications = models.TextField(
        blank=True,
        verbose_name='Certificaciones',
        help_text='Lista de certificaciones separadas por comas'
    )

    # Información de acceso
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Última IP de Acceso'
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        verbose_name='Intentos de Login Fallidos'
    )
    account_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Cuenta Bloqueada Hasta'
    )

    # Preferencias
    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Claro'), ('dark', 'Oscuro')],
        default='light',
        verbose_name='Tema Preferido'
    )
    language_preference = models.CharField(
        max_length=10,
        choices=[('es', 'Español'), ('en', 'Inglés')],
        default='es',
        verbose_name='Idioma Preferido'
    )
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificaciones por Email'
    )

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"


class AuditLog(models.Model):
    """
    Registro de auditoría para seguimiento de acciones
    """
    ACTION_CHOICES = [
        ('create', 'Crear'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('view', 'Ver'),
        ('login', 'Iniciar Sesión'),
        ('logout', 'Cerrar Sesión'),
        ('export', 'Exportar'),
        ('import', 'Importar'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Acción'
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name='Modelo'
    )
    object_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID del Objeto'
    )
    description = models.TextField(
        verbose_name='Descripción'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora'
    )

    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.model_name} ({self.timestamp})"
