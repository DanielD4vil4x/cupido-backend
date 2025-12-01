# apps/match_app/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.profile_app.subapps.profile.models import Perfil
from apps.preferences_app.models import Preference
from apps.auth_app.models import Usuario

from .utils2 import (
    obtener_perfil,
    obtener_preferencias_por_perfil,
    obtener_perfiles_sugeridos,
)


class MatchRecommendationsView(APIView):
    """
    Devuelve una lista de perfiles recomendados para el usuario.

    🔹 En desarrollo dejamos AllowAny para no usar JWT.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # ⚠️ SOLO PARA PRUEBAS: usuario fijo
        try:
            usuario = Usuario.objects.get(email="johan.triana21@unipamplona.edu.co")
        except Usuario.DoesNotExist:
            return Response(
                {"detail": "Usuario de pruebas no exist  e."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1) Perfil del usuario principal
        perfil_usuario = obtener_perfil(usuario.usuario_id)
        if not perfil_usuario:
            return Response(
                {"detail": "El usuario no tiene perfil asociado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2) Preferencias asociadas al perfil
        preferencias = obtener_preferencias_por_perfil(perfil_usuario)
        if not preferencias:
            return Response(
                {"detail": "El usuario no tiene preferencias configuradas."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 3) Obtener perfiles sugeridos + score
        compatibles = obtener_perfiles_sugeridos(
            perfil_usuario,
            preferencias,
            limite=30,
            con_score=True,
        )

        # 4) Cargar info de Usuario para todos los perfiles de una sola vez
        usuario_ids = [perfil_usuario.usuario_id] + [
            p.usuario_id for p, _ in compatibles
        ]
        usuarios = Usuario.objects.filter(usuario_id__in=usuario_ids)
        usuarios_map = {u.usuario_id: u for u in usuarios}

        usuario_principal = usuarios_map.get(perfil_usuario.usuario_id)

        # Info del usuario principal
        user_info = {
            "usuario_id": perfil_usuario.usuario_id,
            "perfil_id": perfil_usuario.perfil_id,
            "nombre": getattr(usuario_principal, "nombres", None) if usuario_principal else None,
            "apellido": getattr(usuario_principal, "apellidos", None) if usuario_principal else None,
            "hobbies": perfil_usuario.hobbies,
            "estatura": perfil_usuario.estatura,
        }

        # ⭐ Info de las preferencias del usuario principal
        preferences_info = {
            "hobbies_preferidos": preferencias.hobbies_preferidos,
            "rango_edad_min": preferencias.rango_edad_min,
            "rango_edad_max": preferencias.rango_edad_max,
            "rango_estatura_min": preferencias.rango_estatura_min,
            "rango_estatura_max": preferencias.rango_estatura_max,
            "ubicacion": preferencias.ubicacion,
            "genero_preferido": preferencias.genero_preferido,
        }

        # 5) Armar results: perfil recomendado + nombre + score
        results = []
        for perfil, score in compatibles:
            u = usuarios_map.get(perfil.usuario_id)
            results.append(
                {
                    "perfil_id": perfil.perfil_id,
                    "usuario_id": perfil.usuario_id,
                    "nombre": getattr(u, "nombres", None) if u else None,
                    "apellido": getattr(u, "apellidos", None) if u else None,
                    "hobbies": perfil.hobbies,
                    "estatura": perfil.estatura,
                    "estado": perfil.estado,
                    "score": score,
                }
            )

        return Response(
            {
                "user": user_info,
                "preferences": preferences_info,  # 👈 aquí se añaden
                "results": results,
            },
            status=status.HTTP_200_OK,
        )



