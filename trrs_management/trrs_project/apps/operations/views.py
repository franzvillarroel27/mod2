"""
Vistas para el módulo de operaciones
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta

from .models import (
    # Capacitaciones
    TrainingCategory, TrainingCourse, TrainingSchedule, EmployeeTraining,
    TrainingMaterial, TrainingEvaluation,
    # Servicios
    ServiceType, ServiceOrder, ServiceTeam, ServiceReport,
    # Cronograma
    OperationPlan, OperationTask,
    # Inventario
    OperationalWarehouse, OperationalItem, OperationalInventory,
    OperationalMovement, OperationalRequest
)


# ==================== CAPACITACIONES ====================

@login_required
def training_list(request):
    """Lista de capacitaciones"""
    trainings = TrainingSchedule.objects.select_related('course').order_by('-start_date')

    # Filtros
    status = request.GET.get('status')
    if status:
        trainings = trainings.filter(status=status)

    category = request.GET.get('category')
    if category:
        trainings = trainings.filter(course__category_id=category)

    search = request.GET.get('search')
    if search:
        trainings = trainings.filter(
            Q(course__name__icontains=search) |
            Q(course__code__icontains=search)
        )

    categories = TrainingCategory.objects.filter(is_active=True)

    context = {
        'trainings': trainings,
        'categories': categories,
        'current_status': status,
        'current_category': category,
    }

    return render(request, 'operations/training_list.html', context)


@login_required
def training_detail(request, pk):
    """Detalle de una capacitación"""
    training = get_object_or_404(TrainingSchedule, pk=pk)

    participants = training.employeetraining_set.select_related('employee').all()

    context = {
        'training': training,
        'participants': participants,
    }

    return render(request, 'operations/training_detail.html', context)


@login_required
def my_trainings(request):
    """Mis capacitaciones"""
    user = request.user

    my_trainings = EmployeeTraining.objects.filter(
        employee=user
    ).select_related('schedule__course').order_by('-schedule__start_date')

    # Capacitaciones que vencen pronto
    expiring_soon = my_trainings.filter(
        status='passed',
        certificate_expiry_date__lte=timezone.now().date() + timedelta(days=60),
        certificate_expiry_date__gte=timezone.now().date()
    )

    context = {
        'my_trainings': my_trainings,
        'expiring_soon': expiring_soon,
    }

    return render(request, 'operations/my_trainings.html', context)


@login_required
def training_enroll(request, training_id):
    """Inscribirse en una capacitación"""
    training = get_object_or_404(TrainingSchedule, pk=training_id)

    if training.is_full():
        messages.error(request, 'Esta capacitación está llena.')
        return redirect('operations:training_detail', pk=training_id)

    # Verificar si ya está inscrito
    if EmployeeTraining.objects.filter(employee=request.user, schedule=training).exists():
        messages.warning(request, 'Ya estás inscrito en esta capacitación.')
        return redirect('operations:training_detail', pk=training_id)

    # Crear inscripción
    EmployeeTraining.objects.create(
        employee=request.user,
        schedule=training,
        status='enrolled'
    )

    messages.success(request, 'Te has inscrito exitosamente en la capacitación.')
    return redirect('operations:training_detail', pk=training_id)


# ==================== SERVICIOS ====================

@login_required
def service_list(request):
    """Lista de órdenes de servicio"""
    services = ServiceOrder.objects.select_related('service_type', 'supervisor').order_by('-created_at')

    # Filtros
    status = request.GET.get('status')
    if status:
        services = services.filter(status=status)

    priority = request.GET.get('priority')
    if priority:
        services = services.filter(priority=priority)

    search = request.GET.get('search')
    if search:
        services = services.filter(
            Q(order_number__icontains=search) |
            Q(client_name__icontains=search) |
            Q(well_name__icontains=search)
        )

    context = {
        'services': services,
        'current_status': status,
        'current_priority': priority,
    }

    return render(request, 'operations/service_list.html', context)


@login_required
def service_detail(request, pk):
    """Detalle de una orden de servicio"""
    service = get_object_or_404(ServiceOrder, pk=pk)

    team = service.serviceteam_set.select_related('employee').all()
    items = service.items.all()

    context = {
        'service': service,
        'team': team,
        'items': items,
    }

    return render(request, 'operations/service_detail.html', context)


# ==================== CRONOGRAMA ====================

@login_required
def operation_plan_list(request):
    """Lista de planes de operación"""
    plans = OperationPlan.objects.select_related('responsible').order_by('-start_date')

    # Filtros
    status = request.GET.get('status')
    if status:
        plans = plans.filter(status=status)

    context = {
        'plans': plans,
        'current_status': status,
    }

    return render(request, 'operations/operation_plan_list.html', context)


@login_required
def operation_plan_detail(request, pk):
    """Detalle de un plan de operación"""
    plan = get_object_or_404(OperationPlan, pk=pk)

    tasks = plan.tasks.select_related('assigned_to').order_by('start_date')

    context = {
        'plan': plan,
        'tasks': tasks,
    }

    return render(request, 'operations/operation_plan_detail.html', context)


@login_required
def operation_calendar(request):
    """Calendario de operaciones"""
    # Obtener tareas para el calendario
    tasks = OperationTask.objects.filter(
        status__in=['pending', 'in_progress']
    ).select_related('operation_plan', 'assigned_to')

    # Convertir a formato FullCalendar
    events = []
    for task in tasks:
        events.append({
            'title': task.name,
            'start': task.start_date.isoformat(),
            'end': task.end_date.isoformat(),
            'backgroundColor': '#007bff' if task.status == 'in_progress' else '#6c757d',
            'url': f"/operations/plans/{task.operation_plan.pk}/"
        })

    context = {
        'events': events,
    }

    return render(request, 'operations/operation_calendar.html', context)


# ==================== INVENTARIO ====================

@login_required
def inventory_list(request):
    """Lista de inventario"""
    items = OperationalItem.objects.prefetch_related('inventory_records').filter(is_active=True)

    # Filtros
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)

    warehouse = request.GET.get('warehouse')
    if warehouse:
        items = items.filter(inventory_records__warehouse_id=warehouse).distinct()

    low_stock = request.GET.get('low_stock')
    if low_stock == '1':
        # Filtrar items con stock bajo
        items = [item for item in items if item.is_low_stock()]

    search = request.GET.get('search')
    if search:
        items = items.filter(
            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(manufacturer__icontains=search)
        )

    warehouses = OperationalWarehouse.objects.filter(is_active=True)

    context = {
        'items': items,
        'warehouses': warehouses,
        'current_category': category,
        'current_warehouse': warehouse,
    }

    return render(request, 'operations/inventory_list.html', context)


@login_required
def inventory_detail(request, pk):
    """Detalle de un item del inventario"""
    item = get_object_or_404(OperationalItem, pk=pk)

    inventory_by_warehouse = item.inventory_records.select_related('warehouse').all()
    recent_movements = item.movements.select_related(
        'from_warehouse', 'to_warehouse', 'processed_by'
    ).order_by('-movement_date')[:20]

    context = {
        'item': item,
        'inventory_by_warehouse': inventory_by_warehouse,
        'recent_movements': recent_movements,
    }

    return render(request, 'operations/inventory_detail.html', context)


@login_required
@permission_required('operations.add_operationalrequest', raise_exception=True)
def inventory_request_create(request):
    """Crear solicitud de material"""
    if request.method == 'POST':
        # Procesar formulario
        # (implementar con forms.py)
        messages.success(request, 'Solicitud creada exitosamente.')
        return redirect('operations:inventory_list')

    warehouses = OperationalWarehouse.objects.filter(is_active=True)
    items = OperationalItem.objects.filter(is_active=True)

    context = {
        'warehouses': warehouses,
        'items': items,
    }

    return render(request, 'operations/inventory_request_create.html', context)


# ==================== API ENDPOINTS (JSON) ====================

@login_required
def api_inventory_stock(request, item_id):
    """API: Obtener stock de un item por almacén"""
    item = get_object_or_404(OperationalItem, pk=item_id)

    inventory_data = []
    for inv in item.inventory_records.select_related('warehouse').all():
        inventory_data.append({
            'warehouse': inv.warehouse.name,
            'quantity': float(inv.quantity),
            'location': inv.location_in_warehouse,
        })

    return JsonResponse({
        'item': {
            'code': item.code,
            'name': item.name,
            'total_stock': float(item.get_total_stock()),
        },
        'inventory': inventory_data
    })


# ==================== PDF DOWNLOADS ====================

@login_required
def download_training_certificate(request, training_id):
    """Descargar certificado de capacitación en PDF"""
    from .utils.pdf_generators import CertificateGenerator

    employee_training = get_object_or_404(
        EmployeeTraining.objects.select_related(
            'employee', 'schedule__course', 'schedule'
        ),
        pk=training_id
    )

    # Verificar que el usuario tenga permiso
    if not (request.user == employee_training.employee or
            request.user.is_staff or
            request.user.can_manage_operations()):
        messages.error(request, 'No tienes permiso para descargar este certificado.')
        return redirect('operations:my_trainings')

    # Verificar que la capacitación esté aprobada
    if employee_training.status != 'passed':
        messages.error(request, 'Esta capacitación aún no está aprobada.')
        return redirect('operations:my_trainings')

    # Generar PDF
    generator = CertificateGenerator(employee_training)
    return generator.get_response()


@login_required
@permission_required('operations.view_serviceorder', raise_exception=True)
def download_service_report(request, service_id):
    """Descargar reporte de servicio en PDF"""
    from .utils.pdf_generators import ServiceReportGenerator

    service_order = get_object_or_404(
        ServiceOrder.objects.select_related('service_type', 'supervisor'),
        pk=service_id
    )

    # Generar PDF
    generator = ServiceReportGenerator(service_order)
    return generator.get_response()


@login_required
@permission_required('operations.view_operationalitem', raise_exception=True)
def download_inventory_report(request):
    """Descargar reporte de inventario en PDF"""
    from .utils.pdf_generators import InventoryReportGenerator

    # Obtener items según filtros
    items = OperationalItem.objects.filter(is_active=True)

    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)

    warehouse = request.GET.get('warehouse')
    if warehouse:
        items = items.filter(inventory_records__warehouse_id=warehouse).distinct()

    low_stock = request.GET.get('low_stock')
    if low_stock == '1':
        items = [item for item in items if item.is_low_stock()]

    # Generar PDF
    title = "Reporte de Inventario Operativo"
    if category:
        title += f" - Categoría: {dict(OperationalItem.CATEGORY_CHOICES).get(category, category)}"

    generator = InventoryReportGenerator(items, title=title)
    return generator.get_response()
