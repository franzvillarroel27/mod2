from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trrs_project.apps.accounts'
    verbose_name = 'Cuentas y Usuarios'

    def ready(self):
        import trrs_project.apps.accounts.signals
