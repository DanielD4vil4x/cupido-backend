# apps/match_app/utils.py
from typing import List, Optional, Set

from apps.profile_app.subapps.profile.models import Perfil
from apps.preferences_app.models import Preference


# Helpers
def normalizar_hobbies(cadena: Optional[str]) -> Set[str]:
    """
    Recibe una cadena tipo: "cine, gym, videojuegos"
    y devuelve un set normalizado en minúsculas.
    """
    if not cadena:
        return set()
    return {h.strip().lower() for h in cadena.split(",") if h.strip()}


# ===============================
# Obtener perfil y preferencias
# ===============================

def obtener_perfil(user_id: int) -> Optional[Perfil]:
    """
    Devuelve el Perfil asociado a un usuario_id (campo usuario_id en la tabla).
    """
    return Perfil.objects.filter(usuario_id=user_id).first()


def obtener_preferencias_por_perfil(perfil: Perfil) -> Optional[Preference]:
    """
    Usa perfil.preferencias_id para buscar el registro en preferences_app_preference.
    (OJO: el campo correcto es 'preferencias', por eso Django crea 'preferencias_id').
    """
    # corregido: estaba escrito 'prefencias_id'
    pref_id = getattr(perfil, "preferencias_id", None)

    if not pref_id:
        return None

    return Preference.objects.filter(id=pref_id).first()


def obtener_otros_perfiles(perfil: Perfil):
    """
    Devuelve un queryset con todos los demás perfiles (distinto usuario_id).
    """
    return Perfil.objects.exclude(usuario_id=perfil.usuario_id)


# ===============================
# Validación de compatibilidad
# ===============================

def perfil_cumple_preferencias(perfil: Perfil, preferencias: Preference) -> bool:
    """
    Devuelve True si el perfil cumple las preferencias mínimas.
    """

    # 1) Rango de estatura
    if preferencias.rango_estatura_min is not None and perfil.estatura is not None:
        if perfil.estatura <= preferencias.rango_estatura_min:
            return False

    if preferencias.rango_estatura_max is not None and perfil.estatura is not None:
        if perfil.estatura >= preferencias.rango_estatura_max:
            return False

    # 2) Hobbies: si hay hobbies preferidos, al menos 1 en común
    pref_hobbies = normalizar_hobbies(preferencias.hobbies_preferidos)
    perfil_hobbies = normalizar_hobbies(perfil.hobbies)

    if pref_hobbies:
        if not (pref_hobbies & perfil_hobbies):
            return False

    # 3) Género / edad
    # En tu modelo Perfil no existen directamente 'genero' ni 'edad',
    # así que usamos getattr para evitar errores si no están.
    genero_perfil = getattr(perfil, "genero", None)
    edad_perfil = getattr(perfil, "edad", None)

    if preferencias.genero_preferido and genero_perfil:
        if genero_perfil != preferencias.genero_preferido:
            return False

    if preferencias.rango_edad_min is not None and edad_perfil is not None:
        if edad_perfil < preferencias.rango_edad_min:
            return False

    if preferencias.rango_edad_max is not None and edad_perfil is not None:
        if edad_perfil > preferencias.rango_edad_max:
            return False

    return True


# ===============================
# Score de compatibilidad
# ===============================

def calcular_score(preferencias: Preference, perfil: Perfil) -> float:
    """
    Calcula un puntaje de compatibilidad simple.
    """
    score = 0.0

    # Hobbies en común
    pref_hobbies = normalizar_hobbies(preferencias.hobbies_preferidos)
    perfil_hobbies = normalizar_hobbies(perfil.hobbies)

    comunes = pref_hobbies & perfil_hobbies
    score += 1 * len(comunes)

    # Estatura dentro de rango suma 1
    if (
        preferencias.rango_estatura_min is not None
        and preferencias.rango_estatura_max is not None
        and perfil.estatura is not None
    ):
        if preferencias.rango_estatura_min <= perfil.estatura <= preferencias.rango_estatura_max:
            score += 1

    # Edad dentro de rango suma 1 (si existe edad en el perfil)
    edad_perfil = getattr(perfil, "edad", None)
    if (
        preferencias.rango_edad_min is not None
        and preferencias.rango_edad_max is not None
        and edad_perfil is not None
    ):
        if preferencias.rango_edad_min <= edad_perfil <= preferencias.rango_edad_max:
            score += 1

    # Género coincide suma 1 (si existe genero en el perfil)
    genero_perfil = getattr(perfil, "genero", None)
    if preferencias.genero_preferido and genero_perfil:
        if genero_perfil == preferencias.genero_preferido:
            score += 1

    return score


# ===============================
# Perfiles sugeridos (feed)
# ===============================

def obtener_perfiles_sugeridos(
    perfil_usuario: Perfil,
    preferencias: Preference,
    limite: int = 30,
    con_score: bool = False,  # ← NUEVO
):
    """
    Devuelve perfiles sugeridos filtrados por preferencias y ordenados por score.

    - Si con_score=False (por defecto): devuelve [Perfil, Perfil, ...]
    - Si con_score=True: devuelve [(Perfil, score), (Perfil, score), ...]
    """
    otros = obtener_otros_perfiles(perfil_usuario)

    compatibles = []
    for p in otros:
        if perfil_cumple_preferencias(p, preferencias):
            score = calcular_score(preferencias, p)
            compatibles.append((p, score))
        else:
            score = calcular_score(preferencias, p)
            if score >= 1:
                compatibles.append((p, score))

    # ordenar por score desc
    compatibles.sort(key=lambda x: x[1], reverse=True)

    if con_score:
        # devolvemos (perfil, score)
        return compatibles[:limite]

    # devolvemos solo los perfiles
    perfiles_ordenados = [p for p, _ in compatibles]
    return perfiles_ordenados[:limite]
