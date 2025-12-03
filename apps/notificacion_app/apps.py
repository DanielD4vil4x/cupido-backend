from django.apps import AppConfig


class NotificacionAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notificacion_app'

    def ready(self):
        import apps.notificacion_app.signals