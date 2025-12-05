"""
Configuración del admin para el módulo de operaciones
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    # Capacitaciones
    TrainingCategory, TrainingCourse, TrainingSchedule,
    EmployeeTraining, TrainingMaterial, TrainingEvaluation,
    # Servicios
    ServiceType, ServiceOrder, ServiceTeam, ServiceItem,
    ServiceReport, ClientFeedback,
    # Cronograma
    OperationPlan, OperationTask, OperationResource,
    OperationLog, OperationRisk,
    # Inventario
    OperationalWarehouse, OperationalItem, OperationalInventory,
    OperationalMovement, OperationalRequest, OperationalRequestItem,
    OperationalTool, ToolUsageHistory
)


# ==================== CAPACITACIONES ====================

@admin.register(TrainingCategory)
class TrainingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_badge', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.name
        )
    color_badge.short_description = 'Color'


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'difficulty', 'duration_hours', 'is_mandatory', 'is_active']
    list_filter = ['category', 'difficulty', 'is_mandatory', 'is_active']
    search_fields = ['code', 'name', 'description']
    filter_horizontal = ['prerequisites']
    fieldsets = (
        ('Información Básica', {
            'fields': ('category', 'code', 'name', 'description', 'difficulty')
        }),
        ('Duración y Validez', {
            'fields': ('duration_hours', 'validity_days', 'is_mandatory')
        }),
        ('Detalles', {
            'fields': ('instructor', 'max_participants', 'prerequisites')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


class EmployeeTrainingInline(admin.TabularInline):
    model = EmployeeTraining
    extra = 1
    fields = ['employee', 'status', 'attendance', 'score']


@admin.register(TrainingSchedule)
class TrainingScheduleAdmin(admin.ModelAdmin):
    list_display = ['course', 'start_date', 'location', 'status', 'available_slots', 'created_by']
    list_filter = ['status', 'start_date']
    search_fields = ['course__name', 'location']
    inlines = [EmployeeTrainingInline]
    readonly_fields = ['created_by', 'created_at']

    def available_slots(self, obj):
        slots = obj.get_available_slots()
        color = 'green' if slots > 5 else 'orange' if slots > 0 else 'red'
        return format_html('<span style="color: {};">{}/{}</span>', color, slots, obj.max_participants)
    available_slots.short_description = 'Disponibles'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmployeeTraining)
class EmployeeTrainingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'schedule', 'status', 'score', 'certificate_number', 'is_expired_badge']
    list_filter = ['status', 'schedule__course__category', 'attendance']
    search_fields = ['employee__username', 'employee__first_name', 'employee__last_name', 'certificate_number']
    readonly_fields = ['certificate_number', 'certificate_issue_date']

    def is_expired_badge(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">✗ Vencido</span>')
        elif obj.certificate_expiry_date:
            days = obj.days_until_expiry()
            if days and days < 30:
                return format_html('<span style="color: orange;">⚠ {} días</span>', days)
        return format_html('<span style="color: green;">✓ Vigente</span>')
    is_expired_badge.short_description = 'Estado'


@admin.register(TrainingMaterial)
class TrainingMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'material_type', 'is_required', 'order']
    list_filter = ['material_type', 'is_required', 'course__category']
    search_fields = ['title', 'course__name']


@admin.register(TrainingEvaluation)
class TrainingEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee_training', 'evaluator', 'evaluation_date', 'score', 'passed']
    list_filter = ['passed', 'evaluation_date']
    search_fields = ['employee_training__employee__username']


# ==================== SERVICIOS ====================

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'base_price', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


class ServiceTeamInline(admin.TabularInline):
    model = ServiceTeam
    extra = 1


class ServiceItemInline(admin.TabularInline):
    model = ServiceItem
    extra = 1


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'service_type', 'client_name', 'status', 'priority_badge', 'start_date', 'supervisor']
    list_filter = ['status', 'priority', 'service_type', 'start_date']
    search_fields = ['order_number', 'client_name', 'well_name']
    inlines = [ServiceTeamInline, ServiceItemInline]
    readonly_fields = ['created_by', 'created_at']
    date_hierarchy = 'start_date'

    def priority_badge(self, obj):
        colors = {'low': '#28a745', 'medium': '#ffc107', 'high': '#fd7e14', 'urgent': '#dc3545'}
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Prioridad'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ['service_order', 'report_date', 'prepared_by', 'objectives_met']
    list_filter = ['objectives_met', 'report_date']
    search_fields = ['service_order__order_number']


@admin.register(ClientFeedback)
class ClientFeedbackAdmin(admin.ModelAdmin):
    list_display = ['service_order', 'rating_stars', 'would_recommend', 'submitted_by', 'submitted_at']
    list_filter = ['rating', 'would_recommend', 'submitted_at']
    search_fields = ['service_order__order_number', 'submitted_by']

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107;">{}</span>', stars)
    rating_stars.short_description = 'Calificación'


# ==================== CRONOGRAMA ====================

class OperationTaskInline(admin.TabularInline):
    model = OperationTask
    extra = 1
    fields = ['name', 'assigned_to', 'start_date', 'end_date', 'status', 'progress_percentage']


@admin.register(OperationPlan)
class OperationPlanAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'status', 'progress_bar', 'start_date', 'end_date', 'responsible']
    list_filter = ['status', 'start_date']
    search_fields = ['code', 'name']
    inlines = [OperationTaskInline]
    readonly_fields = ['created_by', 'created_at']

    def progress_bar(self, obj):
        color = '#28a745' if obj.progress_percentage >= 75 else '#ffc107' if obj.progress_percentage >= 50 else '#dc3545'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white;">{:.0f}%</div>'
            '</div>',
            obj.progress_percentage, color, obj.progress_percentage
        )
    progress_bar.short_description = 'Progreso'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OperationTask)
class OperationTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'operation_plan', 'assigned_to', 'status', 'priority', 'start_date', 'is_overdue_badge']
    list_filter = ['status', 'priority', 'start_date']
    search_fields = ['name', 'operation_plan__code']
    filter_horizontal = ['dependencies']

    def is_overdue_badge(self, obj):
        if obj.is_overdue():
            return format_html('<span style="color: red;">✗ Retrasada</span>')
        return format_html('<span style="color: green;">✓ A tiempo</span>')
    is_overdue_badge.short_description = 'Estado'


@admin.register(OperationResource)
class OperationResourceAdmin(admin.ModelAdmin):
    list_display = ['resource_name', 'resource_type', 'task', 'quantity', 'unit', 'allocated_date']
    list_filter = ['resource_type', 'allocated_date']
    search_fields = ['resource_name', 'task__name']


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['operation_plan', 'task', 'log_date', 'logged_by']
    list_filter = ['log_date', 'operation_plan']
    search_fields = ['entry', 'operation_plan__code']
    readonly_fields = ['created_at']


@admin.register(OperationRisk)
class OperationRiskAdmin(admin.ModelAdmin):
    list_display = ['operation_plan', 'risk_level_badge', 'severity', 'probability', 'status', 'responsible']
    list_filter = ['severity', 'probability', 'status']
    search_fields = ['operation_plan__code', 'risk_description']

    def risk_level_badge(self, obj):
        level = obj.get_risk_level()
        colors = {'critical': '#dc3545', 'high': '#fd7e14', 'medium': '#ffc107', 'low': '#28a745'}
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            colors.get(level, '#6c757d'),
            level.upper()
        )
    risk_level_badge.short_description = 'Nivel de Riesgo'


# ==================== INVENTARIO ====================

@admin.register(OperationalWarehouse)
class OperationalWarehouseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'location', 'manager', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'location']


@admin.register(OperationalItem)
class OperationalItemAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'unit_cost', 'total_stock_display', 'is_low_stock_badge', 'is_critical']
    list_filter = ['category', 'is_active', 'is_critical']
    search_fields = ['code', 'name', 'manufacturer', 'model']

    def total_stock_display(self, obj):
        return f"{obj.get_total_stock()} {obj.unit}"
    total_stock_display.short_description = 'Stock Total'

    def is_low_stock_badge(self, obj):
        if obj.is_low_stock():
            return format_html('<span style="color: red;">⚠ Bajo</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    is_low_stock_badge.short_description = 'Estado Stock'


@admin.register(OperationalInventory)
class OperationalInventoryAdmin(admin.ModelAdmin):
    list_display = ['warehouse', 'item', 'quantity', 'location_in_warehouse', 'last_counted_date']
    list_filter = ['warehouse', 'item__category']
    search_fields = ['item__code', 'item__name', 'warehouse__code']


@admin.register(OperationalMovement)
class OperationalMovementAdmin(admin.ModelAdmin):
    list_display = ['movement_number', 'movement_type', 'item', 'quantity', 'from_warehouse', 'to_warehouse', 'movement_date', 'processed_by']
    list_filter = ['movement_type', 'movement_date']
    search_fields = ['movement_number', 'item__code', 'reference']
    readonly_fields = ['created_at']
    date_hierarchy = 'movement_date'


class OperationalRequestItemInline(admin.TabularInline):
    model = OperationalRequestItem
    extra = 1


@admin.register(OperationalRequest)
class OperationalRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'requested_by', 'warehouse', 'status', 'request_date', 'needed_date']
    list_filter = ['status', 'request_date', 'warehouse']
    search_fields = ['request_number', 'requested_by__username']
    inlines = [OperationalRequestItemInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OperationalTool)
class OperationalToolAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'item', 'current_status', 'assigned_to', 'maintenance_due_badge', 'usage_hours']
    list_filter = ['current_status', 'acquisition_date']
    search_fields = ['serial_number', 'item__code', 'item__name']

    def maintenance_due_badge(self, obj):
        if obj.is_maintenance_due():
            return format_html('<span style="color: red;">⚠ Vencido</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    maintenance_due_badge.short_description = 'Mantenimiento'


@admin.register(ToolUsageHistory)
class ToolUsageHistoryAdmin(admin.ModelAdmin):
    list_display = ['tool', 'user', 'checkout_date', 'checkin_date', 'hours_used', 'condition_checkout', 'condition_checkin']
    list_filter = ['checkout_date', 'condition_checkout', 'condition_checkin']
    search_fields = ['tool__serial_number', 'user__username']
