"""
Modelos comunes del sistema
"""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Modelo de notificaciones personalizadas"""
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('success', 'Éxito'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='custom_notifications',
        verbose_name='Usuario'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='info',
        verbose_name='Tipo'
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    message = models.TextField(verbose_name='Mensaje')
    is_read = models.BooleanField(default=False, verbose_name='Leída')
    link = models.CharField(max_length=300, blank=True, verbose_name='Enlace')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class SystemConfiguration(models.Model):
    """Configuración del sistema"""
    key = models.CharField(max_length=100, unique=True, verbose_name='Clave')
    value = models.TextField(verbose_name='Valor')
    description = models.TextField(blank=True, verbose_name='Descripción')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')

    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'

    def __str__(self):
        return self.key
