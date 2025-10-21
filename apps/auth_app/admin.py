from django.contrib import admin
from legacy_models.models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario_id", "nombres", "email")

