"""
Vistas para el core (dashboard principal)
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from trrs_project.apps.operations.models import (
    ServiceOrder, TrainingSchedule, OperationPlan,
    OperationalInventory, OperationalRequest
)


@login_required
def dashboard_home(request):
    """Dashboard principal con métricas y widgets"""
    user = request.user

    # Métricas de servicios
    services_active = ServiceOrder.objects.filter(
        status='in_progress'
    ).count()

    services_completed_month = ServiceOrder.objects.filter(
        status='completed',
        end_date__gte=timezone.now() - timedelta(days=30)
    ).count()

    # Métricas de capacitaciones
    trainings_upcoming = TrainingSchedule.objects.filter(
        status='confirmed',
        start_date__gte=timezone.now(),
        start_date__lte=timezone.now() + timedelta(days=30)
    ).count()

    # Métricas de operaciones
    operations_active = OperationPlan.objects.filter(
        status='in_progress'
    ).count()

    # Inventario bajo stock
    low_stock_items = OperationalInventory.objects.filter(
        quantity__lte=models.F('item__min_stock')
    ).count()

    # Solicitudes pendientes
    if user.role in ['admin', 'gerente_operaciones']:
        pending_requests = OperationalRequest.objects.filter(
            status='submitted'
        ).count()
    else:
        pending_requests = 0

    # Notificaciones recientes
    recent_notifications = user.custom_notifications.filter(
        is_read=False
    )[:5]

    # Capacitaciones del usuario próximas a vencer
    user_trainings_expiring = []
    if hasattr(user, 'trainings'):
        user_trainings_expiring = user.trainings.filter(
            status='passed',
            certificate_expiry_date__lte=timezone.now().date() + timedelta(days=60),
            certificate_expiry_date__gte=timezone.now().date()
        ).order_by('certificate_expiry_date')[:5]

    context = {
        'services_active': services_active,
        'services_completed_month': services_completed_month,
        'trainings_upcoming': trainings_upcoming,
        'operations_active': operations_active,
        'low_stock_items': low_stock_items,
        'pending_requests': pending_requests,
        'recent_notifications': recent_notifications,
        'user_trainings_expiring': user_trainings_expiring,
    }

    return render(request, 'dashboard/home.html', context)


@login_required
def notifications_view(request):
    """Vista de notificaciones"""
    notifications = request.user.custom_notifications.all()[:50]

    context = {
        'notifications': notifications,
    }

    return render(request, 'core/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Marca una notificación como leída"""
    try:
        notification = request.user.custom_notifications.get(id=notification_id)
        notification.is_read = True
        notification.save()
    except:
        pass

    return redirect('core:notifications')
