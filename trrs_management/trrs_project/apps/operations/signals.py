"""
Signals para el módulo de operaciones
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import (
    EmployeeTraining, TrainingSchedule, OperationalMovement,
    OperationalInventory, OperationalRequest, ServiceOrder,
    OperationTask
)
from notifications.signals import notify


@receiver(post_save, sender=EmployeeTraining)
def generate_certificate_number(sender, instance, created, **kwargs):
    """
    Genera número de certificado cuando se aprueba una capacitación
    """
    if instance.status == 'passed' and not instance.certificate_number:
        # Generar número de certificado único
        year = timezone.now().year
        count = EmployeeTraining.objects.filter(
            status='passed',
            certificate_issue_date__year=year
        ).count()
        instance.certificate_number = f"CERT-{year}-{count+1:05d}"
        instance.certificate_issue_date = timezone.now().date()

        # Calcular fecha de vencimiento
        validity_days = instance.schedule.course.validity_days
        instance.certificate_expiry_date = instance.certificate_issue_date + timedelta(days=validity_days)
        instance.save()


@receiver(post_save, sender=EmployeeTraining)
def notify_training_completion(sender, instance, **kwargs):
    """
    Notifica al empleado cuando completa una capacitación
    """
    if instance.status == 'passed' and instance.certificate_number:
        notify.send(
            sender=instance.schedule.course,
            recipient=instance.employee,
            verb='ha completado la capacitación',
            description=f'Felicidades! Has completado {instance.schedule.course.name}. Certificado: {instance.certificate_number}',
            action_object=instance
        )


@receiver(post_save, sender=OperationalMovement)
def update_inventory_on_movement(sender, instance, created, **kwargs):
    """
    Actualiza el inventario cuando hay un movimiento
    """
    if created:
        # Entrada
        if instance.movement_type == 'in' and instance.to_warehouse:
            inventory, _ = OperationalInventory.objects.get_or_create(
                warehouse=instance.to_warehouse,
                item=instance.item,
                defaults={'quantity': 0}
            )
            inventory.quantity += instance.quantity
            inventory.save()

        # Salida
        elif instance.movement_type == 'out' and instance.from_warehouse:
            inventory = OperationalInventory.objects.get(
                warehouse=instance.from_warehouse,
                item=instance.item
            )
            inventory.quantity -= instance.quantity
            inventory.save()

        # Transferencia
        elif instance.movement_type == 'transfer':
            if instance.from_warehouse:
                from_inv = OperationalInventory.objects.get(
                    warehouse=instance.from_warehouse,
                    item=instance.item
                )
                from_inv.quantity -= instance.quantity
                from_inv.save()

            if instance.to_warehouse:
                to_inv, _ = OperationalInventory.objects.get_or_create(
                    warehouse=instance.to_warehouse,
                    item=instance.item,
                    defaults={'quantity': 0}
                )
                to_inv.quantity += instance.quantity
                to_inv.save()


@receiver(post_save, sender=OperationalInventory)
def check_low_stock(sender, instance, **kwargs):
    """
    Verifica si el stock está bajo y envía notificación
    """
    if instance.quantity <= instance.item.min_stock:
        # Notificar al encargado del almacén
        if instance.warehouse.manager:
            notify.send(
                sender=instance.item,
                recipient=instance.warehouse.manager,
                verb='está bajo en stock',
                description=f'{instance.item.name} en {instance.warehouse.name} tiene solo {instance.quantity} {instance.item.unit}',
                action_object=instance
            )


@receiver(post_save, sender=ServiceOrder)
def generate_service_order_number(sender, instance, created, **kwargs):
    """
    Genera número de orden de servicio automáticamente
    """
    if created and not instance.order_number:
        year = timezone.now().year
        month = timezone.now().month
        count = ServiceOrder.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count()
        instance.order_number = f"OS-{year}{month:02d}-{count+1:04d}"
        instance.save()


@receiver(post_save, sender=OperationTask)
def notify_task_assignment(sender, instance, created, **kwargs):
    """
    Notifica al usuario cuando se le asigna una tarea
    """
    if instance.assigned_to:
        notify.send(
            sender=instance.operation_plan,
            recipient=instance.assigned_to,
            verb='te ha asignado una tarea',
            description=f'Nueva tarea asignada: {instance.name}',
            action_object=instance
        )


@receiver(post_save, sender=OperationTask)
def update_operation_plan_progress(sender, instance, **kwargs):
    """
    Actualiza el progreso del plan de operación cuando cambia una tarea
    """
    instance.operation_plan.update_progress()


@receiver(post_save, sender=OperationalRequest)
def notify_request_approval(sender, instance, **kwargs):
    """
    Notifica cuando se aprueba/rechaza una solicitud
    """
    if instance.status == 'approved' and instance.approved_by:
        notify.send(
            sender=instance.approved_by,
            recipient=instance.requested_by,
            verb='aprobó tu solicitud',
            description=f'Solicitud {instance.request_number} aprobada',
            action_object=instance
        )
    elif instance.status == 'rejected' and instance.approved_by:
        notify.send(
            sender=instance.approved_by,
            recipient=instance.requested_by,
            verb='rechazó tu solicitud',
            description=f'Solicitud {instance.request_number} rechazada',
            action_object=instance
        )
