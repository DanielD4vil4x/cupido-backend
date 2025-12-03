
from django.contrib import admin
from .models import notificacion

@admin.register(notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'usuario_destino', 'estado', 'fecha_envio')
    list_filter = ('tipo', 'estado', 'fecha_envio')
    search_fields = ('mensaje', 'usuario_destino')
    readonly_fields = ('fecha_envio',)
