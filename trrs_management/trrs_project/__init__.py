# TR&RS Management System
# Sistema de Gestión Integral para TR&RS

# Configuración de Celery
from __future__ import absolute_import, unicode_literals

# Esto asegura que la app de Celery se cargue cuando Django inicie
from .celery import app as celery_app

__all__ = ('celery_app',)
