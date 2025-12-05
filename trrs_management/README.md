# TR&RS Management System

Sistema de Gestión Integral para TR&RS - Soluciones para la Industria Petrolera

## 📋 Descripción

Sistema completo de gestión empresarial desarrollado en Django 4.x que integra múltiples módulos para la administración de operaciones, mantenimiento, HSEQ, compras y recursos humanos.

## 🚀 Características Principales

### 1. **Módulo de Operaciones**
- ✅ **Gestión de Capacitaciones**
  - Categorías y cursos de capacitación
  - Programación y calendario de capacitaciones
  - Registro de asistencia y evaluaciones
  - Generación automática de certificados
  - Control de vencimientos y renovaciones
  - Material de apoyo (PDFs, videos, presentaciones)

- ✅ **Gestión de Servicios**
  - Órdenes de servicio (Casing Running, Tubing Running, etc.)
  - Asignación de equipos y recursos
  - Seguimiento de horas/hombre
  - Reportes de servicio
  - Retroalimentación de clientes

- ✅ **Cronograma de Operaciones**
  - Planes de operación con tareas
  - Calendario interactivo
  - Dependencias entre tareas
  - Seguimiento de progreso
  - Análisis de riesgos
  - Bitácora de operaciones

- ✅ **Inventario Operativo**
  - Gestión de almacenes
  - Control de stock con alertas de stock mínimo
  - Movimientos de inventario (entradas, salidas, transferencias)
  - Solicitudes de material con flujo de aprobación
  - Herramientas y equipos con historial de uso
  - Códigos QR y códigos de barras

### 2. **Sistema de Autenticación y Permisos**
- ✅ Modelo de usuario personalizado
- ✅ Roles de usuario:
  - Administrador
  - Gerente de Operaciones
  - Supervisor de Mantenimiento
  - Coordinador HSEQ
  - Comprador
  - Técnico/Operador
  - Visitante
- ✅ Perfiles de usuario con información extendida
- ✅ Log de auditoría completo
- ✅ Control de acceso basado en permisos

### 3. **Dashboard Principal**
- ✅ Métricas clave (KPIs) personalizadas por rol
- ✅ Widgets de notificaciones
- ✅ Alertas de vencimientos
- ✅ Accesos rápidos a funciones frecuentes

### 4. **Sistema de Notificaciones**
- ✅ Notificaciones en tiempo real
- ✅ Alertas de vencimientos de certificaciones
- ✅ Alertas de stock bajo
- ✅ Notificaciones de asignación de tareas

### 5. **API REST**
- ✅ API completa con Django REST Framework
- ✅ Serializers para todos los modelos principales
- ✅ Autenticación por token
- ✅ Documentación con Swagger/OpenAPI
- ✅ Filtros, búsqueda y paginación

## 🛠️ Stack Tecnológico

### Backend
- **Django 4.2.7** - Framework web
- **Python 3.11** - Lenguaje de programación
- **PostgreSQL** - Base de datos principal
- **Redis** - Caché y message broker
- **Celery** - Tareas asíncronas y programadas

### Frontend
- **Bootstrap 5** - Framework CSS
- **JavaScript** - Interactividad
- **FullCalendar** - Calendario interactivo
- **DataTables** - Tablas dinámicas

### Librerías Adicionales
- **Django REST Framework** - API REST
- **Celery Beat** - Tareas programadas
- **ReportLab / WeasyPrint** - Generación de PDFs
- **django-notifications-hq** - Sistema de notificaciones
- **django-qr-code** - Generación de códigos QR
- **Pillow** - Procesamiento de imágenes

## 📁 Estructura del Proyecto

```
trrs_management/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── media/
│   ├── documents/
│   └── photos/
├── templates/
│   ├── base/
│   ├── dashboard/
│   ├── accounts/
│   └── operations/
└── trrs_project/
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    ├── celery.py
    └── apps/
        ├── accounts/       # Usuarios y autenticación
        ├── core/           # Dashboard y funcionalidades comunes
        ├── operations/     # Módulo de operaciones
        ├── maintenance/    # Módulo de mantenimiento
        ├── hseq/           # Módulo HSEQ
        ├── purchases/      # Módulo de compras
        ├── hr/             # Recursos humanos
        └── reports/        # Reportes y dashboards
```

## 🔧 Instalación y Configuración

### Requisitos Previos
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker y Docker Compose (opcional)

### Instalación con Docker (Recomendado)

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd trrs_management
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Construir y levantar los contenedores:**
```bash
docker-compose up -d --build
```

4. **Ejecutar migraciones:**
```bash
docker-compose exec web python manage.py migrate
```

5. **Crear superusuario:**
```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Acceder a la aplicación:**
- Web: http://localhost:8000
- Admin: http://localhost:8000/admin
- API Docs: http://localhost:8000/swagger

### Instalación Manual

1. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar base de datos PostgreSQL:**
```bash
# Crear base de datos
createdb trrs_db
```

4. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar migraciones:**
```bash
python manage.py migrate
```

6. **Crear superusuario:**
```bash
python manage.py createsuperuser
```

7. **Iniciar servidor de desarrollo:**
```bash
python manage.py runserver
```

8. **En otra terminal, iniciar Celery:**
```bash
celery -A trrs_project worker -l info
celery -A trrs_project beat -l info
```

## 📊 Modelos de Datos Principales

### Módulo de Operaciones

#### Capacitaciones
- `TrainingCategory` - Categorías de capacitación
- `TrainingCourse` - Cursos disponibles
- `TrainingSchedule` - Programación de capacitaciones
- `EmployeeTraining` - Capacitaciones por empleado
- `TrainingMaterial` - Material de apoyo
- `TrainingEvaluation` - Evaluaciones

#### Servicios
- `ServiceType` - Tipos de servicio
- `ServiceOrder` - Órdenes de servicio
- `ServiceTeam` - Equipo asignado
- `ServiceItem` - Items del servicio
- `ServiceReport` - Reportes de servicio
- `ClientFeedback` - Retroalimentación del cliente

#### Cronograma
- `OperationPlan` - Planes de operación
- `OperationTask` - Tareas específicas
- `OperationResource` - Recursos asignados
- `OperationLog` - Bitácora de operaciones
- `OperationRisk` - Análisis de riesgos

#### Inventario
- `OperationalWarehouse` - Almacenes
- `OperationalItem` - Items del inventario
- `OperationalInventory` - Stock actual
- `OperationalMovement` - Movimientos de inventario
- `OperationalRequest` - Solicitudes de material
- `OperationalTool` - Herramientas y equipos
- `ToolUsageHistory` - Historial de uso

### Autenticación
- `User` - Usuario personalizado con roles
- `UserProfile` - Perfil extendido del usuario
- `AuditLog` - Registro de auditoría

## 🔌 API REST Endpoints

### Capacitaciones
```
GET    /api/v1/trainings/categories/
GET    /api/v1/trainings/courses/
GET    /api/v1/trainings/schedules/
GET    /api/v1/trainings/employee-trainings/
POST   /api/v1/trainings/enroll/
```

### Servicios
```
GET    /api/v1/services/types/
GET    /api/v1/services/orders/
POST   /api/v1/services/orders/
GET    /api/v1/services/orders/{id}/
PUT    /api/v1/services/orders/{id}/
```

### Inventario
```
GET    /api/v1/inventory/items/
GET    /api/v1/inventory/items/{id}/stock/
GET    /api/v1/inventory/movements/
POST   /api/v1/inventory/movements/
```

## 🔐 Seguridad

- ✅ Protección CSRF
- ✅ Protección XSS
- ✅ HTTPS obligatorio en producción
- ✅ Validación de entrada de datos
- ✅ Logs de auditoría completos
- ✅ Autenticación segura con hash de contraseñas
- ✅ Sesiones con timeout configurado

## 📝 Tareas Programadas (Celery Beat)

- **Diario 8:00 AM** - Verificar vencimientos de capacitaciones
- **Lunes 7:00 AM** - Enviar recordatorios de mantenimiento preventivo
- **Cada 6 horas** - Verificar stock bajo en inventario
- **Viernes 6:00 PM** - Generar reporte semanal de operaciones
- **Primer día del mes 2:00 AM** - Limpiar notificaciones antiguas

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
python manage.py test

# Con pytest
pytest

# Con coverage
coverage run -m pytest
coverage report
```

## 📦 Deployment

### Producción con Docker

```bash
# Construir para producción
docker-compose -f docker-compose.prod.yml up -d --build

# Colectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Ejecutar migraciones
docker-compose exec web python manage.py migrate
```

## 🤝 Contribución

Este es un proyecto privado para TR&RS. Para contribuir:

1. Crear una rama feature
2. Hacer commits descriptivos
3. Crear Pull Request
4. Esperar revisión del equipo

## 📄 Licencia

Propietario - TR&RS © 2024. Todos los derechos reservados.

## 👥 Equipo de Desarrollo

- **Backend**: Sistema Django completo con modelos, vistas y API
- **Frontend**: Templates Bootstrap 5 responsive
- **DevOps**: Configuración Docker y deployment

## 📞 Soporte

Para soporte técnico, contactar a: soporte@trrs.com

## 🗺️ Roadmap

### Fase 1 - Completada ✅
- [x] Configuración inicial del proyecto
- [x] Modelos de datos completos
- [x] Sistema de autenticación y permisos
- [x] Módulo de operaciones (capacitaciones, servicios, cronograma, inventario)
- [x] API REST básica

### Fase 2 - En Progreso 🔄
- [ ] Templates HTML completos con Bootstrap 5
- [ ] Dashboard interactivo con gráficos
- [ ] Calendario interactivo (FullCalendar)
- [ ] Tablas dinámicas con filtros (DataTables)
- [ ] Sistema de notificaciones en tiempo real

### Fase 3 - Pendiente 📋
- [ ] Generación de reportes PDF
- [ ] Módulo de mantenimiento completo
- [ ] Módulo HSEQ completo
- [ ] Módulo de compras completo
- [ ] Módulo de recursos humanos completo
- [ ] Integración con sistemas externos
- [ ] App móvil (React Native)

## 🔧 Comandos Útiles

```bash
# Crear nueva app
python manage.py startapp nombre_app

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Colectar archivos estáticos
python manage.py collectstatic

# Iniciar shell de Django
python manage.py shell

# Ejecutar Celery worker
celery -A trrs_project worker -l info

# Ejecutar Celery beat
celery -A trrs_project beat -l info

# Ver tareas programadas
celery -A trrs_project inspect scheduled
```

## 📚 Documentación Adicional

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)

---

**Desarrollado con ❤️ para TR&RS**
