from django.apps import AppConfig


class NotificacionAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificacion_app'

    def ready(self):
        import notificacion_app.signals