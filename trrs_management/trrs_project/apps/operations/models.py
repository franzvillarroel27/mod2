"""
Modelos para el módulo de operaciones
Incluye: Capacitaciones, Servicios, Cronograma e Inventario
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


# ==================== CAPACITACIONES ====================

class TrainingCategory(models.Model):
    """Categorías de capacitaciones"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icono')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Color')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoría de Capacitación'
        verbose_name_plural = 'Categorías de Capacitación'
        ordering = ['name']

    def __str__(self):
        return self.name


class TrainingCourse(models.Model):
    """Cursos de capacitación disponibles"""
    DIFFICULTY_CHOICES = [
        ('basic', 'Básico'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
    ]

    category = models.ForeignKey(
        TrainingCategory,
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name='Categoría'
    )
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name='Nombre del Curso')
    description = models.TextField(verbose_name='Descripción')
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='basic',
        verbose_name='Dificultad'
    )
    duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Duración (horas)'
    )
    validity_days = models.IntegerField(
        default=365,
        verbose_name='Validez (días)',
        help_text='Días antes de que venza la certificación'
    )
    is_mandatory = models.BooleanField(
        default=False,
        verbose_name='Obligatorio'
    )
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name='Prerequisitos'
    )
    instructor = models.CharField(max_length=200, blank=True, verbose_name='Instructor')
    max_participants = models.IntegerField(
        default=20,
        verbose_name='Máximo de Participantes'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Curso de Capacitación'
        verbose_name_plural = 'Cursos de Capacitación'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class TrainingSchedule(models.Model):
    """Cronograma de capacitaciones"""
    STATUS_CHOICES = [
        ('planned', 'Planificada'),
        ('confirmed', 'Confirmada'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]

    course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.PROTECT,
        related_name='schedules',
        verbose_name='Curso'
    )
    start_date = models.DateTimeField(verbose_name='Fecha de Inicio')
    end_date = models.DateTimeField(verbose_name='Fecha de Fin')
    location = models.CharField(max_length=200, verbose_name='Ubicación')
    instructor = models.CharField(max_length=200, verbose_name='Instructor')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name='Estado'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='EmployeeTraining',
        related_name='training_schedules',
        verbose_name='Participantes'
    )
    max_participants = models.IntegerField(verbose_name='Máximo de Participantes')
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_trainings',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Programación de Capacitación'
        verbose_name_plural = 'Programaciones de Capacitación'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.course.name} - {self.start_date.strftime('%Y-%m-%d')}"

    def get_available_slots(self):
        """Retorna espacios disponibles"""
        enrolled = self.employeetraining_set.filter(status='enrolled').count()
        return self.max_participants - enrolled

    def is_full(self):
        """Verifica si está lleno"""
        return self.get_available_slots() <= 0


class EmployeeTraining(models.Model):
    """Relación entre empleados y capacitaciones"""
    STATUS_CHOICES = [
        ('enrolled', 'Inscrito'),
        ('attended', 'Asistió'),
        ('passed', 'Aprobado'),
        ('failed', 'Reprobado'),
        ('cancelled', 'Cancelado'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainings',
        verbose_name='Empleado'
    )
    schedule = models.ForeignKey(
        TrainingSchedule,
        on_delete=models.CASCADE,
        verbose_name='Programación'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='enrolled',
        verbose_name='Estado'
    )
    attendance = models.BooleanField(default=False, verbose_name='Asistencia')
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Calificación'
    )
    certificate_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número de Certificado'
    )
    certificate_issue_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Emisión'
    )
    certificate_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Vencimiento'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Capacitación de Empleado'
        verbose_name_plural = 'Capacitaciones de Empleados'
        unique_together = ['employee', 'schedule']
        ordering = ['-schedule__start_date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.schedule.course.name}"

    def is_expired(self):
        """Verifica si la certificación está vencida"""
        if self.certificate_expiry_date:
            return timezone.now().date() > self.certificate_expiry_date
        return False

    def days_until_expiry(self):
        """Días hasta el vencimiento"""
        if self.certificate_expiry_date:
            delta = self.certificate_expiry_date - timezone.now().date()
            return delta.days
        return None


class TrainingMaterial(models.Model):
    """Material de apoyo para capacitaciones"""
    MATERIAL_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('presentation', 'Presentación'),
        ('document', 'Documento'),
        ('link', 'Enlace Externo'),
    ]

    course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name='Curso'
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    material_type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPE_CHOICES,
        verbose_name='Tipo de Material'
    )
    file = models.FileField(
        upload_to='training/materials/',
        blank=True,
        null=True,
        verbose_name='Archivo'
    )
    url = models.URLField(blank=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Descripción')
    order = models.IntegerField(default=0, verbose_name='Orden')
    is_required = models.BooleanField(default=True, verbose_name='Obligatorio')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Material de Capacitación'
        verbose_name_plural = 'Materiales de Capacitación'
        ordering = ['course', 'order', 'title']

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class TrainingEvaluation(models.Model):
    """Evaluaciones de capacitación"""
    employee_training = models.ForeignKey(
        EmployeeTraining,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name='Capacitación del Empleado'
    )
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Evaluador'
    )
    evaluation_date = models.DateField(verbose_name='Fecha de Evaluación')
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Calificación'
    )
    comments = models.TextField(blank=True, verbose_name='Comentarios')
    passed = models.BooleanField(default=False, verbose_name='Aprobado')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Evaluación de Capacitación'
        verbose_name_plural = 'Evaluaciones de Capacitación'
        ordering = ['-evaluation_date']

    def __str__(self):
        return f"Evaluación - {self.employee_training.employee.get_full_name()}"


# ==================== SERVICIOS ====================

class ServiceType(models.Model):
    """Tipos de servicio"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    description = models.TextField(blank=True, verbose_name='Descripción')
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Precio Base'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Servicio'
        verbose_name_plural = 'Tipos de Servicio'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class ServiceOrder(models.Model):
    """Órdenes de servicio"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('on_hold', 'En Espera'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]

    order_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de Orden'
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Tipo de Servicio'
    )
    client_name = models.CharField(max_length=200, verbose_name='Nombre del Cliente')
    client_contact = models.CharField(max_length=100, verbose_name='Contacto del Cliente')
    client_phone = models.CharField(max_length=20, verbose_name='Teléfono del Cliente')
    client_email = models.EmailField(blank=True, verbose_name='Email del Cliente')

    location = models.CharField(max_length=300, verbose_name='Ubicación')
    well_name = models.CharField(max_length=100, blank=True, verbose_name='Nombre del Pozo')

    start_date = models.DateTimeField(verbose_name='Fecha de Inicio')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Fin')
    estimated_duration_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='Duración Estimada (horas)'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Prioridad'
    )

    description = models.TextField(verbose_name='Descripción del Servicio')
    special_requirements = models.TextField(
        blank=True,
        verbose_name='Requerimientos Especiales'
    )

    assigned_team = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ServiceTeam',
        related_name='service_orders',
        verbose_name='Equipo Asignado'
    )

    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supervised_services',
        verbose_name='Supervisor'
    )

    total_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name='Total Horas'
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Costo Total'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_service_orders',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Orden de Servicio'
        verbose_name_plural = 'Órdenes de Servicio'
        ordering = ['-created_at']
        permissions = [
            ('can_approve_service', 'Puede aprobar servicios'),
            ('can_cancel_service', 'Puede cancelar servicios'),
        ]

    def __str__(self):
        return f"{self.order_number} - {self.client_name}"

    def get_duration(self):
        """Calcula la duración real del servicio"""
        if self.end_date and self.start_date:
            delta = self.end_date - self.start_date
            return delta.total_seconds() / 3600  # Horas
        return 0


class ServiceTeam(models.Model):
    """Equipo asignado a un servicio"""
    ROLE_CHOICES = [
        ('supervisor', 'Supervisor'),
        ('operator', 'Operador'),
        ('technician', 'Técnico'),
        ('helper', 'Ayudante'),
    ]

    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        verbose_name='Orden de Servicio'
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Empleado'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Rol'
    )
    hours_worked = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='Horas Trabajadas'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Miembro del Equipo de Servicio'
        verbose_name_plural = 'Equipo de Servicio'
        unique_together = ['service_order', 'employee']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.service_order.order_number}"


class ServiceItem(models.Model):
    """Items/equipos utilizados en un servicio"""
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Orden de Servicio'
    )
    item_name = models.CharField(max_length=200, verbose_name='Nombre del Item')
    item_code = models.CharField(max_length=50, blank=True, verbose_name='Código')
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad'
    )
    unit = models.CharField(max_length=20, verbose_name='Unidad')
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Precio Unitario'
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Precio Total'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item de Servicio'
        verbose_name_plural = 'Items de Servicio'

    def __str__(self):
        return f"{self.item_name} - {self.service_order.order_number}"

    def save(self, *args, **kwargs):
        """Calcula el precio total automáticamente"""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class ServiceReport(models.Model):
    """Reporte de servicio"""
    service_order = models.OneToOneField(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name='report',
        verbose_name='Orden de Servicio'
    )
    report_date = models.DateField(verbose_name='Fecha del Reporte')
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Preparado por'
    )

    # Detalles del servicio
    work_performed = models.TextField(verbose_name='Trabajo Realizado')
    equipment_used = models.TextField(verbose_name='Equipos Utilizados')
    materials_consumed = models.TextField(verbose_name='Materiales Consumidos')

    # Resultados
    objectives_met = models.BooleanField(default=True, verbose_name='Objetivos Cumplidos')
    incidents = models.TextField(blank=True, verbose_name='Incidentes')
    observations = models.TextField(blank=True, verbose_name='Observaciones')
    recommendations = models.TextField(blank=True, verbose_name='Recomendaciones')

    # Tiempos
    start_time = models.DateTimeField(verbose_name='Hora de Inicio')
    end_time = models.DateTimeField(verbose_name='Hora de Fin')
    downtime_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='Horas de Paro'
    )
    downtime_reason = models.TextField(blank=True, verbose_name='Razón del Paro')

    # Firmas
    client_signature = models.ImageField(
        upload_to='service/signatures/',
        blank=True,
        null=True,
        verbose_name='Firma del Cliente'
    )
    supervisor_signature = models.ImageField(
        upload_to='service/signatures/',
        blank=True,
        null=True,
        verbose_name='Firma del Supervisor'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reporte de Servicio'
        verbose_name_plural = 'Reportes de Servicio'
        ordering = ['-report_date']

    def __str__(self):
        return f"Reporte - {self.service_order.order_number}"


class ClientFeedback(models.Model):
    """Retroalimentación del cliente"""
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name='Orden de Servicio'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Calificación'
    )
    comments = models.TextField(verbose_name='Comentarios')
    would_recommend = models.BooleanField(
        default=True,
        verbose_name='Recomendaría el Servicio'
    )
    submitted_by = models.CharField(max_length=200, verbose_name='Enviado por')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Envío')

    class Meta:
        verbose_name = 'Retroalimentación del Cliente'
        verbose_name_plural = 'Retroalimentación de Clientes'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Feedback - {self.service_order.order_number} ({self.rating}/5)"


# ==================== CRONOGRAMA DE OPERACIONES ====================

class OperationPlan(models.Model):
    """Plan de operaciones"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('approved', 'Aprobado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nombre del Plan')
    code = models.CharField(max_length=50, unique=True, verbose_name='Código')
    description = models.TextField(verbose_name='Descripción')

    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(verbose_name='Fecha de Fin')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )

    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Porcentaje de Progreso'
    )

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='operation_plans',
        verbose_name='Responsable'
    )

    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Presupuesto'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_operation_plans',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plan de Operación'
        verbose_name_plural = 'Planes de Operación'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def update_progress(self):
        """Actualiza el progreso basado en las tareas"""
        tasks = self.tasks.all()
        if tasks.exists():
            total_progress = sum(task.progress_percentage for task in tasks)
            self.progress_percentage = total_progress / tasks.count()
            self.save()


class OperationTask(models.Model):
    """Tareas específicas del plan de operaciones"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('blocked', 'Bloqueada'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    operation_plan = models.ForeignKey(
        OperationPlan,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Plan de Operación'
    )

    name = models.CharField(max_length=200, verbose_name='Nombre de la Tarea')
    description = models.TextField(verbose_name='Descripción')

    start_date = models.DateTimeField(verbose_name='Fecha de Inicio')
    end_date = models.DateTimeField(verbose_name='Fecha de Fin')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Prioridad'
    )

    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Porcentaje de Progreso'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tasks',
        verbose_name='Asignado a'
    )

    dependencies = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name='Dependencias'
    )

    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='Horas Estimadas'
    )
    actual_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='Horas Reales'
    )

    notes = models.TextField(blank=True, verbose_name='Notas')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tarea de Operación'
        verbose_name_plural = 'Tareas de Operación'
        ordering = ['start_date']

    def __str__(self):
        return f"{self.operation_plan.code} - {self.name}"

    def is_overdue(self):
        """Verifica si la tarea está retrasada"""
        if self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.end_date
        return False


class OperationResource(models.Model):
    """Recursos asignados a operaciones"""
    RESOURCE_TYPE_CHOICES = [
        ('equipment', 'Equipo'),
        ('material', 'Material'),
        ('personnel', 'Personal'),
        ('vehicle', 'Vehículo'),
    ]

    task = models.ForeignKey(
        OperationTask,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='Tarea'
    )

    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        verbose_name='Tipo de Recurso'
    )
    resource_name = models.CharField(max_length=200, verbose_name='Nombre del Recurso')
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad'
    )
    unit = models.CharField(max_length=20, verbose_name='Unidad')

    allocated_date = models.DateField(verbose_name='Fecha de Asignación')
    return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Devolución'
    )

    notes = models.TextField(blank=True, verbose_name='Notas')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Recurso de Operación'
        verbose_name_plural = 'Recursos de Operación'

    def __str__(self):
        return f"{self.resource_name} - {self.task.name}"


class OperationLog(models.Model):
    """Bitácora de operaciones"""
    operation_plan = models.ForeignKey(
        OperationPlan,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Plan de Operación'
    )
    task = models.ForeignKey(
        OperationTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tarea'
    )

    log_date = models.DateTimeField(verbose_name='Fecha del Registro')
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Registrado por'
    )

    entry = models.TextField(verbose_name='Entrada')

    attachments = models.FileField(
        upload_to='operations/logs/',
        blank=True,
        null=True,
        verbose_name='Archivos Adjuntos'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Entrada de Bitácora'
        verbose_name_plural = 'Bitácora de Operaciones'
        ordering = ['-log_date']

    def __str__(self):
        return f"Log - {self.operation_plan.code} - {self.log_date}"


class OperationRisk(models.Model):
    """Análisis de riesgos de operaciones"""
    SEVERITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    PROBABILITY_CHOICES = [
        ('rare', 'Rara'),
        ('unlikely', 'Improbable'),
        ('possible', 'Posible'),
        ('likely', 'Probable'),
        ('certain', 'Segura'),
    ]

    operation_plan = models.ForeignKey(
        OperationPlan,
        on_delete=models.CASCADE,
        related_name='risks',
        verbose_name='Plan de Operación'
    )

    risk_description = models.TextField(verbose_name='Descripción del Riesgo')

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        verbose_name='Severidad'
    )
    probability = models.CharField(
        max_length=20,
        choices=PROBABILITY_CHOICES,
        verbose_name='Probabilidad'
    )

    mitigation_plan = models.TextField(verbose_name='Plan de Mitigación')
    contingency_plan = models.TextField(
        blank=True,
        verbose_name='Plan de Contingencia'
    )

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Responsable'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('identified', 'Identificado'),
            ('mitigated', 'Mitigado'),
            ('closed', 'Cerrado'),
        ],
        default='identified',
        verbose_name='Estado'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Riesgo de Operación'
        verbose_name_plural = 'Riesgos de Operación'
        ordering = ['-created_at']

    def __str__(self):
        return f"Riesgo - {self.operation_plan.code}"

    def get_risk_level(self):
        """Calcula el nivel de riesgo combinado"""
        severity_weight = {
            'low': 1, 'medium': 2, 'high': 3, 'critical': 4
        }
        probability_weight = {
            'rare': 1, 'unlikely': 2, 'possible': 3, 'likely': 4, 'certain': 5
        }

        risk_score = severity_weight.get(self.severity, 0) * probability_weight.get(self.probability, 0)

        if risk_score >= 12:
            return 'critical'
        elif risk_score >= 8:
            return 'high'
        elif risk_score >= 4:
            return 'medium'
        else:
            return 'low'


# ==================== INVENTARIO OPERATIVO ====================

class OperationalWarehouse(models.Model):
    """Almacenes operativos"""
    name = models.CharField(max_length=200, verbose_name='Nombre del Almacén')
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    location = models.CharField(max_length=300, verbose_name='Ubicación')
    description = models.TextField(blank=True, verbose_name='Descripción')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_warehouses',
        verbose_name='Encargado'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Almacén Operativo'
        verbose_name_plural = 'Almacenes Operativos'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class OperationalItem(models.Model):
    """Items del inventario operativo"""
    CATEGORY_CHOICES = [
        ('tool', 'Herramienta'),
        ('equipment', 'Equipo'),
        ('material', 'Material'),
        ('consumable', 'Consumible'),
        ('ppe', 'EPP'),
    ]

    UNIT_CHOICES = [
        ('pcs', 'Piezas'),
        ('kg', 'Kilogramos'),
        ('m', 'Metros'),
        ('l', 'Litros'),
        ('box', 'Cajas'),
        ('set', 'Juegos'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='Categoría'
    )

    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Fabricante'
    )
    model = models.CharField(max_length=100, blank=True, verbose_name='Modelo')

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        verbose_name='Unidad de Medida'
    )

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Costo Unitario'
    )

    min_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Stock Mínimo'
    )
    max_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Stock Máximo'
    )
    reorder_point = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Punto de Reorden'
    )

    barcode = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        null=True,
        verbose_name='Código de Barras'
    )
    qr_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Código QR'
    )

    photo = models.ImageField(
        upload_to='inventory/items/',
        blank=True,
        null=True,
        verbose_name='Foto'
    )

    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_critical = models.BooleanField(default=False, verbose_name='Crítico')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Item Operativo'
        verbose_name_plural = 'Items Operativos'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_total_stock(self):
        """Obtiene el stock total en todos los almacenes"""
        return self.inventory_records.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    def is_low_stock(self):
        """Verifica si está bajo en stock"""
        return self.get_total_stock() <= self.min_stock


class OperationalInventory(models.Model):
    """Stock actual en cada almacén"""
    warehouse = models.ForeignKey(
        OperationalWarehouse,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name='Almacén'
    )
    item = models.ForeignKey(
        OperationalItem,
        on_delete=models.CASCADE,
        related_name='inventory_records',
        verbose_name='Item'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Cantidad'
    )
    location_in_warehouse = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ubicación en Almacén'
    )
    last_counted_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Última Fecha de Conteo'
    )
    last_counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Último Conteo por'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventario Operativo'
        verbose_name_plural = 'Inventarios Operativos'
        unique_together = ['warehouse', 'item']
        indexes = [
            models.Index(fields=['warehouse', 'item']),
        ]

    def __str__(self):
        return f"{self.warehouse.code} - {self.item.code}: {self.quantity} {self.item.unit}"


class OperationalMovement(models.Model):
    """Movimientos de inventario"""
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Entrada'),
        ('out', 'Salida'),
        ('transfer', 'Transferencia'),
        ('adjustment', 'Ajuste'),
        ('return', 'Devolución'),
    ]

    movement_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de Movimiento'
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
        verbose_name='Tipo de Movimiento'
    )

    item = models.ForeignKey(
        OperationalItem,
        on_delete=models.PROTECT,
        related_name='movements',
        verbose_name='Item'
    )

    from_warehouse = models.ForeignKey(
        OperationalWarehouse,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='outgoing_movements',
        verbose_name='Desde Almacén'
    )
    to_warehouse = models.ForeignKey(
        OperationalWarehouse,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='incoming_movements',
        verbose_name='Hacia Almacén'
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad'
    )

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Costo Unitario'
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Costo Total'
    )

    movement_date = models.DateTimeField(verbose_name='Fecha de Movimiento')

    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Referencia'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Procesado por'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-movement_date']
        indexes = [
            models.Index(fields=['-movement_date']),
            models.Index(fields=['item', '-movement_date']),
        ]

    def __str__(self):
        return f"{self.movement_number} - {self.get_movement_type_display()}"

    def save(self, *args, **kwargs):
        """Calcula el costo total automáticamente"""
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)


class OperationalRequest(models.Model):
    """Solicitudes de material"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('submitted', 'Enviada'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
        ('fulfilled', 'Cumplida'),
        ('cancelled', 'Cancelada'),
    ]

    request_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de Solicitud'
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='material_requests',
        verbose_name='Solicitado por'
    )

    warehouse = models.ForeignKey(
        OperationalWarehouse,
        on_delete=models.PROTECT,
        verbose_name='Almacén'
    )

    request_date = models.DateTimeField(verbose_name='Fecha de Solicitud')
    needed_date = models.DateField(verbose_name='Fecha Requerida')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )

    purpose = models.TextField(verbose_name='Propósito')
    notes = models.TextField(blank=True, verbose_name='Notas')

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests',
        verbose_name='Aprobado por'
    )
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Aprobación'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Solicitud de Material'
        verbose_name_plural = 'Solicitudes de Material'
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.request_number} - {self.requested_by.get_full_name()}"


class OperationalRequestItem(models.Model):
    """Items de una solicitud"""
    request = models.ForeignKey(
        OperationalRequest,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Solicitud'
    )
    item = models.ForeignKey(
        OperationalItem,
        on_delete=models.PROTECT,
        verbose_name='Item'
    )
    quantity_requested = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad Solicitada'
    )
    quantity_approved = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Cantidad Aprobada'
    )
    quantity_delivered = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Cantidad Entregada'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Item de Solicitud'
        verbose_name_plural = 'Items de Solicitud'

    def __str__(self):
        return f"{self.request.request_number} - {self.item.name}"


class OperationalTool(models.Model):
    """Herramientas y equipos especiales"""
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('in_use', 'En Uso'),
        ('maintenance', 'En Mantenimiento'),
        ('damaged', 'Dañada'),
        ('retired', 'Retirada'),
    ]

    item = models.OneToOneField(
        OperationalItem,
        on_delete=models.CASCADE,
        verbose_name='Item'
    )

    serial_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Número de Serie'
    )

    acquisition_date = models.DateField(verbose_name='Fecha de Adquisición')
    acquisition_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Costo de Adquisición'
    )

    current_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='Estado Actual'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tools',
        verbose_name='Asignada a'
    )
    assignment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Asignación'
    )

    last_maintenance_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Última Fecha de Mantenimiento'
    )
    next_maintenance_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Próxima Fecha de Mantenimiento'
    )

    calibration_due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Calibración'
    )

    warranty_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Vencimiento de Garantía'
    )

    usage_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Horas de Uso'
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Ubicación Actual'
    )

    notes = models.TextField(blank=True, verbose_name='Notas')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Herramienta/Equipo'
        verbose_name_plural = 'Herramientas y Equipos'
        ordering = ['serial_number']

    def __str__(self):
        return f"{self.item.code} - {self.serial_number}"

    def is_maintenance_due(self):
        """Verifica si requiere mantenimiento"""
        if self.next_maintenance_date:
            return timezone.now().date() >= self.next_maintenance_date
        return False

    def is_calibration_due(self):
        """Verifica si requiere calibración"""
        if self.calibration_due_date:
            return timezone.now().date() >= self.calibration_due_date
        return False


class ToolUsageHistory(models.Model):
    """Historial de uso de herramientas"""
    tool = models.ForeignKey(
        OperationalTool,
        on_delete=models.CASCADE,
        related_name='usage_history',
        verbose_name='Herramienta'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario'
    )

    checkout_date = models.DateTimeField(verbose_name='Fecha de Salida')
    checkin_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Devolución'
    )

    purpose = models.TextField(verbose_name='Propósito')

    condition_checkout = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excelente'),
            ('good', 'Buena'),
            ('fair', 'Regular'),
            ('poor', 'Mala'),
        ],
        verbose_name='Condición al Salir'
    )
    condition_checkin = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excelente'),
            ('good', 'Buena'),
            ('fair', 'Regular'),
            ('poor', 'Mala'),
        ],
        blank=True,
        verbose_name='Condición al Regresar'
    )

    hours_used = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='Horas Usadas'
    )

    notes = models.TextField(blank=True, verbose_name='Notas')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Historial de Uso de Herramienta'
        verbose_name_plural = 'Historiales de Uso de Herramientas'
        ordering = ['-checkout_date']

    def __str__(self):
        return f"{self.tool.serial_number} - {self.user.get_full_name()} ({self.checkout_date})"
