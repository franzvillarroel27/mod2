"""
Serializers para la API REST del módulo de operaciones
"""

from rest_framework import serializers
from trrs_project.apps.operations.models import (
    TrainingCategory, TrainingCourse, TrainingSchedule, EmployeeTraining,
    ServiceType, ServiceOrder, OperationPlan, OperationTask,
    OperationalItem, OperationalInventory, OperationalMovement
)


# ==================== CAPACITACIONES ====================

class TrainingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCategory
        fields = ['id', 'name', 'description', 'icon', 'color', 'is_active']


class TrainingCourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = TrainingCourse
        fields = [
            'id', 'category', 'category_name', 'code', 'name', 'description',
            'difficulty', 'duration_hours', 'validity_days', 'is_mandatory',
            'instructor', 'max_participants', 'is_active'
        ]


class TrainingScheduleSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    available_slots = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSchedule
        fields = [
            'id', 'course', 'course_name', 'start_date', 'end_date',
            'location', 'instructor', 'status', 'max_participants',
            'available_slots', 'notes'
        ]

    def get_available_slots(self, obj):
        return obj.get_available_slots()


class EmployeeTrainingSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    course_name = serializers.CharField(source='schedule.course.name', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeTraining
        fields = [
            'id', 'employee', 'employee_name', 'schedule', 'course_name',
            'status', 'attendance', 'score', 'certificate_number',
            'certificate_issue_date', 'certificate_expiry_date',
            'is_expired'
        ]

    def get_is_expired(self, obj):
        return obj.is_expired()


# ==================== SERVICIOS ====================

class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'code', 'description', 'base_price', 'is_active']


class ServiceOrderSerializer(serializers.ModelSerializer):
    service_type_name = serializers.CharField(source='service_type.name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True)

    class Meta:
        model = ServiceOrder
        fields = [
            'id', 'order_number', 'service_type', 'service_type_name',
            'client_name', 'client_contact', 'client_phone', 'client_email',
            'location', 'well_name', 'start_date', 'end_date',
            'estimated_duration_hours', 'status', 'priority',
            'description', 'supervisor', 'supervisor_name',
            'total_hours', 'total_cost'
        ]
        read_only_fields = ['order_number']


# ==================== CRONOGRAMA ====================

class OperationPlanSerializer(serializers.ModelSerializer):
    responsible_name = serializers.CharField(source='responsible.get_full_name', read_only=True)
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = OperationPlan
        fields = [
            'id', 'name', 'code', 'description', 'start_date', 'end_date',
            'status', 'progress_percentage', 'responsible', 'responsible_name',
            'budget', 'task_count'
        ]

    def get_task_count(self, obj):
        return obj.tasks.count()


class OperationTaskSerializer(serializers.ModelSerializer):
    operation_plan_name = serializers.CharField(source='operation_plan.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = OperationTask
        fields = [
            'id', 'operation_plan', 'operation_plan_name', 'name',
            'description', 'start_date', 'end_date', 'status', 'priority',
            'progress_percentage', 'assigned_to', 'assigned_to_name',
            'estimated_hours', 'actual_hours', 'is_overdue'
        ]

    def get_is_overdue(self, obj):
        return obj.is_overdue()


# ==================== INVENTARIO ====================

class OperationalItemSerializer(serializers.ModelSerializer):
    total_stock = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = OperationalItem
        fields = [
            'id', 'code', 'name', 'description', 'category',
            'manufacturer', 'model', 'unit', 'unit_cost',
            'min_stock', 'max_stock', 'reorder_point',
            'barcode', 'is_active', 'is_critical',
            'total_stock', 'is_low_stock'
        ]

    def get_total_stock(self, obj):
        return float(obj.get_total_stock())

    def get_is_low_stock(self, obj):
        return obj.is_low_stock()


class OperationalInventorySerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    item_code = serializers.CharField(source='item.code', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = OperationalInventory
        fields = [
            'id', 'warehouse', 'warehouse_name', 'item', 'item_code',
            'item_name', 'quantity', 'location_in_warehouse',
            'last_counted_date', 'updated_at'
        ]


class OperationalMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)

    class Meta:
        model = OperationalMovement
        fields = [
            'id', 'movement_number', 'movement_type', 'item', 'item_name',
            'from_warehouse', 'from_warehouse_name', 'to_warehouse',
            'to_warehouse_name', 'quantity', 'unit_cost', 'total_cost',
            'movement_date', 'reference', 'notes', 'processed_by',
            'processed_by_name'
        ]
        read_only_fields = ['movement_number', 'total_cost']
