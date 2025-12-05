from django.apps import AppConfig


class OperationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trrs_project.apps.operations'
    verbose_name = 'Operaciones'

    def ready(self):
        import trrs_project.apps.operations.signals
