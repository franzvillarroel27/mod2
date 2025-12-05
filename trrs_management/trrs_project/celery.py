"""
Celery configuration for TR&RS Management System
"""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Configurar el módulo de settings por defecto para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trrs_project.settings')

app = Celery('trrs_project')

# Usar namespace 'CELERY' en settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubrir tareas automáticamente en todas las apps
app.autodiscover_tasks()

# Configuración de tareas periódicas
app.conf.beat_schedule = {
    # Verificar vencimientos de capacitaciones cada día a las 8 AM
    'check-training-expiration': {
        'task': 'trrs_project.apps.operations.tasks.check_training_expiration',
        'schedule': crontab(hour=8, minute=0),
    },
    # Enviar recordatorios de mantenimiento preventivo
    'send-maintenance-reminders': {
        'task': 'trrs_project.apps.maintenance.tasks.send_maintenance_reminders',
        'schedule': crontab(hour=7, minute=0, day_of_week='monday'),
    },
    # Verificar stock bajo en inventario cada 6 horas
    'check-low-stock': {
        'task': 'trrs_project.apps.operations.tasks.check_low_stock',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    # Generar reporte semanal de operaciones
    'generate-weekly-report': {
        'task': 'trrs_project.apps.reports.tasks.generate_weekly_operations_report',
        'schedule': crontab(hour=18, minute=0, day_of_week='friday'),
    },
    # Limpiar notificaciones antiguas (más de 30 días)
    'cleanup-old-notifications': {
        'task': 'trrs_project.apps.core.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0, day_of_month=1),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tarea de debugging"""
    print(f'Request: {self.request!r}')
