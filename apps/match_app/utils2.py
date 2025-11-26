# match_app/utils.py
from typing import List, Optional, Set

from .models import Perfil
from preferences_app.models import Preference


# Helpers

def normalizar_hobbies(cadena: Optional[str]) -> Set[str]:
    if not cadena:
        return set()
    return {h.strip().lower() for h in cadena.split(",") if h.strip()}


# Obtener perfil y preferencias


def obtener_perfil(user_id: int) -> Optional[Perfil]:
    """
    Devuelve el Perfil asociado a un usuario_id (campo usuario_id en la tabla).
    """
    return Perfil.objects.filter(usuario_id=user_id).first()


def obtener_preferencias_por_perfil(perfil: Perfil) -> Optional[Preference]:
    """
    Usa perfil.prefencias_id para buscar el registro en preferences_app_preference.
    """
    if not perfil.prefencias_id:
        return None

    return Preference.objects.filter(id=perfil.prefencias_id).first()


def obtener_otros_perfiles(perfil: Perfil):
    """
    Devuelve un queryset con todos los demás perfiles (distinto usuario_id).
    """
    return Perfil.objects.exclude(usuario_id=perfil.usuario_id)



# Validación de compatibilidad

def perfil_cumple_preferencias(perfil: Perfil, preferencias: Preference) -> bool:
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

    # 3) Ubicación: depende de tu diseño.
    # Si Preference.ubicacion guarda algo tipo "Bogotá" y tú todavía no tienes
    # ese string en Perfil (solo ubicacion_id), puedes dejar esto comentado
    # hasta que conectes con la tabla de ubicación.

    # 4) Género / edad también dependen de en qué modelo están,
    if preferencias.genero_preferido and perfil.genero:
        if perfil.genero != preferencias.genero_preferido:
            return False
    
    if preferencias.rango_edad_min and perfil.edad:
        if perfil.edad < preferencias.rango_edad_min:
            return False
    
    if preferencias.rango_edad_max and perfil.edad:
        if perfil.edad > preferencias.rango_edad_max:
            return False

    return True

# Score de compatibilidad

def calcular_score(preferencias: Preference, perfil: Perfil) -> float:
    score = 0.0

    # Hobbies en común
    pref_hobbies = normalizar_hobbies(preferencias.hobbies_preferidos)
    perfil_hobbies = normalizar_hobbies(perfil.hobbies)

    comunes = pref_hobbies & perfil_hobbies
    score += 1 * len(comunes)

    # egtatura
    if preferencias.rango_estatura_max is not None and perfil.estatura is not None:
        if perfil.estatura <= preferencias.rango_estatura_max:
            if preferencias.rango_estatura_min is not None and perfil.estatura is not None:
                if perfil.estatura >= preferencias.rango_estatura_min:
                    score += 1
    
    # edad
    if preferencias.rango_edad_max is not None and perfil.edad is not None:
        if perfil.edad <= preferencias.rango_edad_max:
            if preferencias.rango_edad_min is not None and perfil.edad is not None:
                if perfil.edad >= preferencias.rango_edad_min:
                    score += 1
    
    #genero y sus 39 tipos de gey
    if preferencias.genero_preferido and perfil.genero:
        if perfil.genero == preferencias.genero_preferido:
            score += 1

        
    return score

# Perfiles sugeridos (feed)

def obtener_perfiles_sugeridos(
    perfil_usuario: Perfil,
    preferencias: Preference,
    limite: int = 30,
):
    """
    Devuelve una lista de Perfiles sugeridos, filtrados por preferencias
    y ordenados por score de compatibilidad.
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

    # devolver solo los perfiles
    perfiles_ordenados = [p for p, _ in compatibles]
    return perfiles_ordenados[:limite]
