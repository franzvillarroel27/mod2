"""
Formularios para el módulo de operaciones
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Field
from crispy_forms.bootstrap import FormActions

from .models import (
    TrainingSchedule, TrainingCourse, EmployeeTraining,
    ServiceOrder, ServiceType,
    OperationPlan, OperationTask,
    OperationalItem, OperationalMovement, OperationalRequest,
    OperationalRequestItem
)


# ==================== CAPACITACIONES ====================

class TrainingScheduleForm(forms.ModelForm):
    """Formulario para programar capacitaciones"""

    class Meta:
        model = TrainingSchedule
        fields = [
            'course', 'start_date', 'end_date', 'location',
            'instructor', 'max_participants', 'status', 'notes'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sala de Capacitación A'}),
            'instructor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del instructor'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('course', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            Row(
                Column('start_date', css_class='col-md-6'),
                Column('end_date', css_class='col-md-6'),
            ),
            Row(
                Column('location', css_class='col-md-6'),
                Column('instructor', css_class='col-md-6'),
            ),
            'max_participants',
            'notes',
            FormActions(
                Submit('submit', 'Guardar Capacitación', css_class='btn btn-primary'),
                HTML('<a href="{% url \'operations:training_list\' %}" class="btn btn-secondary">Cancelar</a>'),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        course = cleaned_data.get('course')

        # Validar que la fecha de inicio sea futura
        if start_date and start_date < timezone.now():
            raise ValidationError('La fecha de inicio debe ser futura.')

        # Validar que la fecha de fin sea posterior a la de inicio
        if start_date and end_date:
            if end_date <= start_date:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

            # Validar que la duración coincida aproximadamente con el curso
            if course:
                duration_hours = (end_date - start_date).total_seconds() / 3600
                expected_hours = float(course.duration_hours)

                # Permitir variación del 20%
                if abs(duration_hours - expected_hours) > expected_hours * 0.2:
                    self.add_error('end_date',
                        f'La duración ({duration_hours:.1f}h) no coincide con la duración del curso ({expected_hours}h).'
                    )

        return cleaned_data


class EmployeeTrainingEnrollForm(forms.ModelForm):
    """Formulario para inscribir empleados en capacitaciones"""

    class Meta:
        model = EmployeeTraining
        fields = ['employee', 'schedule', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', None)
        super().__init__(*args, **kwargs)

        if self.schedule:
            self.fields['schedule'].initial = self.schedule
            self.fields['schedule'].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'schedule',
            'employee',
            'notes',
            FormActions(
                Submit('submit', 'Inscribir', css_class='btn btn-success'),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        schedule = cleaned_data.get('schedule')

        if employee and schedule:
            # Verificar si ya está inscrito
            if EmployeeTraining.objects.filter(employee=employee, schedule=schedule).exists():
                raise ValidationError(f'{employee.get_full_name()} ya está inscrito en esta capacitación.')

            # Verificar si hay cupos disponibles
            if schedule.is_full():
                raise ValidationError('Esta capacitación ya está llena.')

        return cleaned_data


class TrainingEvaluationForm(forms.Form):
    """Formulario para evaluar empleados en capacitaciones"""
    score = forms.DecimalField(
        min_value=0,
        max_value=100,
        decimal_places=2,
        label='Calificación',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    comments = forms.CharField(
        required=False,
        label='Comentarios',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    passed = forms.BooleanField(
        required=False,
        initial=False,
        label='Aprobado',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score < 0 or score > 100:
            raise ValidationError('La calificación debe estar entre 0 y 100.')
        return score


# ==================== SERVICIOS ====================

class ServiceOrderForm(forms.ModelForm):
    """Formulario para crear órdenes de servicio"""

    class Meta:
        model = ServiceOrder
        fields = [
            'service_type', 'client_name', 'client_contact', 'client_phone', 'client_email',
            'location', 'well_name', 'start_date', 'estimated_duration_hours',
            'priority', 'description', 'special_requirements', 'supervisor'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'estimated_duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0.5, 'step': 0.5}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'special_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5 class="mb-3"><i class="fas fa-info-circle me-2"></i>Información del Servicio</h5>'),
            Row(
                Column('service_type', css_class='col-md-6'),
                Column('priority', css_class='col-md-6'),
            ),
            'description',

            HTML('<h5 class="mb-3 mt-4"><i class="fas fa-user me-2"></i>Información del Cliente</h5>'),
            Row(
                Column('client_name', css_class='col-md-6'),
                Column('client_contact', css_class='col-md-6'),
            ),
            Row(
                Column('client_phone', css_class='col-md-6'),
                Column('client_email', css_class='col-md-6'),
            ),

            HTML('<h5 class="mb-3 mt-4"><i class="fas fa-map-marker-alt me-2"></i>Ubicación y Programación</h5>'),
            Row(
                Column('location', css_class='col-md-6'),
                Column('well_name', css_class='col-md-6'),
            ),
            Row(
                Column('start_date', css_class='col-md-6'),
                Column('estimated_duration_hours', css_class='col-md-6'),
            ),
            'supervisor',
            'special_requirements',

            FormActions(
                Submit('submit', 'Crear Orden de Servicio', css_class='btn btn-primary btn-lg'),
                HTML('<a href="{% url \'operations:service_list\' %}" class="btn btn-secondary">Cancelar</a>'),
            )
        )

    def clean_client_email(self):
        email = self.cleaned_data.get('client_email')
        if email and '@' not in email:
            raise ValidationError('Ingrese un correo electrónico válido.')
        return email

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < timezone.now():
            raise ValidationError('La fecha de inicio debe ser futura.')
        return start_date


# ==================== CRONOGRAMA ====================

class OperationPlanForm(forms.ModelForm):
    """Formulario para crear planes de operación"""

    class Meta:
        model = OperationPlan
        fields = [
            'name', 'code', 'description', 'start_date', 'end_date',
            'responsible', 'budget', 'status'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

        return cleaned_data


class OperationTaskForm(forms.ModelForm):
    """Formulario para crear tareas de operación"""

    class Meta:
        model = OperationTask
        fields = [
            'operation_plan', 'name', 'description', 'start_date', 'end_date',
            'status', 'priority', 'assigned_to', 'estimated_hours', 'dependencies'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0.5, 'step': 0.5}),
        }

    def __init__(self, *args, **kwargs):
        self.operation_plan = kwargs.pop('operation_plan', None)
        super().__init__(*args, **kwargs)

        if self.operation_plan:
            self.fields['operation_plan'].initial = self.operation_plan
            self.fields['operation_plan'].widget = forms.HiddenInput()

            # Filtrar dependencias para solo mostrar tareas del mismo plan
            self.fields['dependencies'].queryset = OperationTask.objects.filter(
                operation_plan=self.operation_plan
            )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        operation_plan = cleaned_data.get('operation_plan')

        if start_date and end_date and end_date <= start_date:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')

        # Validar que las fechas estén dentro del rango del plan
        if operation_plan:
            if start_date and start_date.date() < operation_plan.start_date:
                self.add_error('start_date', 'La fecha de inicio no puede ser anterior al inicio del plan.')

            if end_date and end_date.date() > operation_plan.end_date:
                self.add_error('end_date', 'La fecha de fin no puede ser posterior al fin del plan.')

        return cleaned_data


# ==================== INVENTARIO ====================

class OperationalItemForm(forms.ModelForm):
    """Formulario para registrar items del inventario"""

    class Meta:
        model = OperationalItem
        fields = [
            'code', 'name', 'description', 'category', 'manufacturer', 'model',
            'unit', 'unit_cost', 'min_stock', 'max_stock', 'reorder_point',
            'barcode', 'photo', 'is_critical'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reorder_point': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5 class="mb-3">Información Básica</h5>'),
            Row(
                Column('code', css_class='col-md-4'),
                Column('name', css_class='col-md-8'),
            ),
            'description',
            Row(
                Column('category', css_class='col-md-6'),
                Column('unit', css_class='col-md-6'),
            ),
            Row(
                Column('manufacturer', css_class='col-md-6'),
                Column('model', css_class='col-md-6'),
            ),

            HTML('<h5 class="mb-3 mt-4">Costos y Stock</h5>'),
            Row(
                Column('unit_cost', css_class='col-md-6'),
                Column('is_critical', css_class='col-md-6'),
            ),
            Row(
                Column('min_stock', css_class='col-md-4'),
                Column('max_stock', css_class='col-md-4'),
                Column('reorder_point', css_class='col-md-4'),
            ),

            HTML('<h5 class="mb-3 mt-4">Identificación</h5>'),
            Row(
                Column('barcode', css_class='col-md-6'),
                Column('photo', css_class='col-md-6'),
            ),

            FormActions(
                Submit('submit', 'Guardar Item', css_class='btn btn-success'),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        min_stock = cleaned_data.get('min_stock')
        max_stock = cleaned_data.get('max_stock')
        reorder_point = cleaned_data.get('reorder_point')

        if min_stock and max_stock and min_stock >= max_stock:
            raise ValidationError('El stock mínimo debe ser menor que el stock máximo.')

        if reorder_point:
            if min_stock and reorder_point < min_stock:
                self.add_error('reorder_point', 'El punto de reorden debe ser mayor o igual al stock mínimo.')
            if max_stock and reorder_point > max_stock:
                self.add_error('reorder_point', 'El punto de reorden debe ser menor o igual al stock máximo.')

        return cleaned_data


class OperationalMovementForm(forms.ModelForm):
    """Formulario para registrar movimientos de inventario"""

    class Meta:
        model = OperationalMovement
        fields = [
            'movement_type', 'item', 'from_warehouse', 'to_warehouse',
            'quantity', 'unit_cost', 'movement_date', 'reference', 'notes'
        ]
        widgets = {
            'movement_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        from_warehouse = cleaned_data.get('from_warehouse')
        to_warehouse = cleaned_data.get('to_warehouse')
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')

        # Validar según el tipo de movimiento
        if movement_type == 'in':
            if not to_warehouse:
                self.add_error('to_warehouse', 'Debe especificar el almacén de destino para una entrada.')
        elif movement_type == 'out':
            if not from_warehouse:
                self.add_error('from_warehouse', 'Debe especificar el almacén de origen para una salida.')
        elif movement_type == 'transfer':
            if not from_warehouse or not to_warehouse:
                raise ValidationError('Debe especificar ambos almacenes para una transferencia.')
            if from_warehouse == to_warehouse:
                raise ValidationError('Los almacenes de origen y destino deben ser diferentes.')

        # Validar stock disponible para salidas y transferencias
        if movement_type in ['out', 'transfer'] and from_warehouse and item and quantity:
            try:
                from .models import OperationalInventory
                inventory = OperationalInventory.objects.get(warehouse=from_warehouse, item=item)
                if inventory.quantity < quantity:
                    raise ValidationError(
                        f'Stock insuficiente en {from_warehouse.name}. '
                        f'Disponible: {inventory.quantity} {item.unit}'
                    )
            except OperationalInventory.DoesNotExist:
                raise ValidationError(f'El item no existe en el almacén {from_warehouse.name}.')

        return cleaned_data


class OperationalRequestForm(forms.ModelForm):
    """Formulario para crear solicitudes de material"""

    class Meta:
        model = OperationalRequest
        fields = ['warehouse', 'needed_date', 'purpose', 'notes']
        widgets = {
            'needed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_needed_date(self):
        needed_date = self.cleaned_data.get('needed_date')
        if needed_date and needed_date < timezone.now().date():
            raise ValidationError('La fecha requerida debe ser futura.')
        return needed_date


# ==================== FILTROS ====================

class TrainingFilterForm(forms.Form):
    """Formulario de filtros para capacitaciones"""
    status = forms.ChoiceField(
        choices=[('', 'Todos')] + TrainingSchedule.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=TrainingCourse.objects.none(),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre o código...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import TrainingCategory
        self.fields['category'].queryset = TrainingCategory.objects.filter(is_active=True)


class InventoryFilterForm(forms.Form):
    """Formulario de filtros para inventario"""
    category = forms.ChoiceField(
        choices=[('', 'Todas')] + OperationalItem.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    warehouse = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='Todos los almacenes',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    low_stock = forms.BooleanField(
        required=False,
        label='Solo items bajo stock',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código, nombre o fabricante...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import OperationalWarehouse
        self.fields['warehouse'].queryset = OperationalWarehouse.objects.filter(is_active=True)
