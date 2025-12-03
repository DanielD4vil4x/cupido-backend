from django.db import models
from django.conf import settings # Para traer el modelo de Usuario

# --- MODELO TEMPORAL DE MATCH ---
# Esto es solo un placeholder para que la app de chat pueda funcionar.

class Match(models.Model):
    usuarioA = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_usuario_a"
    )
    usuarioB = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_usuario_b"
    )

    # Agregamos los campos que tu diagrama mencionaba
    fechaMatch = models.DateTimeField(auto_now_add=True)
    estadoMatch = models.CharField(max_length=50, default="activo")

    def __str__(self):
        return f"Match temporal entre {self.usuarioA} y {self.usuarioB}"