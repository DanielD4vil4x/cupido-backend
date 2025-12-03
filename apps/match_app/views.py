# apps/match_app/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.profile_app.subapps.profile.models import Perfil
from apps.preferences_app.models import Preference
from apps.auth_app.models import Usuario

from .utils import (
    obtener_perfil,
    obtener_preferencias_por_perfil,
    obtener_perfiles_sugeridos,
)


class MatchRecommendationsView(APIView):
    """
    Devuelve una lista de perfiles recomendados para el usuario autenticado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 1) Usuario autenticado (JWT)
        usuario: Usuario = request.user  # instancia de auth_app.Usuario

        # 2) Perfil asociado a ese usuario
        perfil_usuario = obtener_perfil(usuario.usuario_id)
        if not perfil_usuario:
            return Response(
                {"detail": "El usuario no tiene perfil asociado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 3) Preferencias asociadas al perfil
        preferencias = obtener_preferencias_por_perfil(perfil_usuario)
        if not preferencias:
            return Response(
                {"detail": "El usuario no tiene preferencias configuradas."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 4) Obtener perfiles sugeridos + score
        compatibles = obtener_perfiles_sugeridos(
            perfil_usuario,
            preferencias,
            limite=30,
            con_score=True,
        )

        # 5) Cargar info de Usuario para todos los perfiles de una sola vez
        usuario_ids = [perfil_usuario.usuario_id] + [
            p.usuario_id for p, _ in compatibles
        ]
        usuarios = Usuario.objects.filter(usuario_id__in=usuario_ids)
        usuarios_map = {u.usuario_id: u for u in usuarios}

        usuario_principal = usuarios_map.get(perfil_usuario.usuario_id)

        # ===== info del usuario principal =====
        # ubicacion del perfil (si es FK)
        ubicacion_obj = getattr(perfil_usuario, "ubicacion", None)
        ubicacion_nombre = None
        if ubicacion_obj is not None:
            # ajusta "nombre" si tu modelo la llama diferente
            ubicacion_nombre = getattr(ubicacion_obj, "nombre", str(ubicacion_obj))

        user_info = {
            "usuario_id": perfil_usuario.usuario_id,
            "perfil_id": perfil_usuario.perfil_id,
            "nombre": getattr(usuario_principal, "nombres", None)
            if usuario_principal
            else None,
            "apellido": getattr(usuario_principal, "apellidos", None)
            if usuario_principal
            else None,
            "hobbies": perfil_usuario.hobbies,
            "estatura": perfil_usuario.estatura,
            # NUEVO: descripción, edad y ubicación
            "descripcion": getattr(perfil_usuario, "descripcion", None),
            "edad": getattr(perfil_usuario, "edad", None),
            "ubicacion": ubicacion_nombre,
        }

        # ===== info de las preferencias del usuario =====
        preferences_info = {
            "hobbies_preferidos": preferencias.hobbies_preferidos,
            "rango_edad_min": preferencias.rango_edad_min,
            "rango_edad_max": preferencias.rango_edad_max,
            "rango_estatura_min": preferencias.rango_estatura_min,
            "rango_estatura_max": preferencias.rango_estatura_max,
            "ubicacion": preferencias.ubicacion,
            "genero_preferido": preferencias.genero_preferido,
        }

        # ===== results: perfiles recomendados =====
        results = []
        for perfil, score in compatibles:
            u = usuarios_map.get(perfil.usuario_id)

            # ubicacion del recomendado
            ubicacion_obj = getattr(perfil, "ubicacion", None)
            ubicacion_nombre = None
            if ubicacion_obj is not None:
                ubicacion_nombre = getattr(ubicacion_obj, "nombre", str(ubicacion_obj))

            results.append(
                {
                    "perfil_id": perfil.perfil_id,
                    "usuario_id": perfil.usuario_id,
                    "nombre": getattr(u, "nombres", None) if u else None,
                    "apellido": getattr(u, "apellidos", None) if u else None,
                    "hobbies": perfil.hobbies,
                    "estatura": perfil.estatura,
                    "estado": perfil.estado,
                    # NUEVO:
                    "descripcion": getattr(perfil, "descripcion", None),
                    "edad": getattr(perfil, "edad", None),
                    "ubicacion": ubicacion_nombre,
                    "score": score,
                }
            )

        return Response(
            {
                "user": user_info,
                "preferences": preferences_info,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )



