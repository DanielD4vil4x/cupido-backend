# apps/match_app/utils.py
from typing import List, Optional, Set
import json

from apps.profile_app.subapps.profile.models import Perfil
from apps.preferences_app.models import Preference
from apps.auth_app.models import Usuario   # 👈 IMPORTANTE

# =========================================
# Helpers
# =========================================

def normalizar_hobbies(cadena: Optional[str]) -> Set[str]:
    if not cadena:
        return set()

    cadena = cadena.strip()

    # Si parece una lista JSON, intentamos parsearla
    if cadena.startswith("[") and cadena.endswith("]"):
        try:
            items = json.loads(cadena)
        except Exception:
            # si falla el JSON, caemos al split normal
            items = cadena.split(",")
    else:
        items = cadena.split(",")

    return {h.strip().lower() for h in items if str(h).strip()}


def obtener_usuario_de_perfil(perfil: Perfil) -> Optional[Usuario]:
    """
    Devuelve el Usuario dueño de este perfil.
    Intenta usar la relación FK 'usuario' y, si no existe, cae a usuario_id.
    """
    usuario = getattr(perfil, "usuario", None)
    if usuario is not None:
        return usuario

    user_id = getattr(perfil, "usuario_id", None)
    if user_id is None:
        return None

    return Usuario.objects.filter(usuario_id=user_id).first()


def genero_coincide_con_preferencia(perfil: Perfil, preferencias: Preference) -> bool:
    """
    Verifica si el género del usuario de este perfil coincide con genero_preferido.

    Reglas:
      - genero_preferido = 'Mujer'  -> solo genero_id = 2
      - genero_preferido = 'Hombre'-> solo genero_id = 1
      - genero_preferido = 'Otros'/'Otro' -> acepta 1, 2 y 3 (no filtra)
      - genero_preferido vacío/raro -> no filtra (True)
    """
    pref = (preferencias.genero_preferido or "").strip().lower()
    if not pref:
        # Sin preferencia explícita -> no filtramos por género
        return True

    usuario = obtener_usuario_de_perfil(perfil)
    if not usuario:
        # Sin usuario no podemos saber género -> mejor descartarlo
        return False

    # Ajusta esta línea si el campo se llama distinto (por ejemplo "genero")
    genero_id = getattr(usuario, "genero_id", None)
    if genero_id is None:
        return False

    if pref == "mujer":
        return genero_id == 2
    if pref == "hombre":
        return genero_id == 1
    if pref in ("otros", "otro"):
        # Acepta cualquier género (1, 2, 3)
        return genero_id in {1, 2, 3}

    # Si llega aquí es un valor raro -> no filtramos estrictamente
    return True


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
    Devuelve True si el perfil cumple las preferencias mínimas (filtros duros).
    """

    # 0) Género: filtro duro obligatorio
    if not genero_coincide_con_preferencia(perfil, preferencias):
        return False

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

    # 3) Edad (si está en el perfil)
    edad_perfil = getattr(perfil, "edad", None)

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

    Regla importante:
      - Si el género NO coincide con genero_preferido, el score es 0 SIEMPRE.
        Así nunca pasa el filtro de "score >= 1".
    """
    # Género obligatorio para cualquier puntaje
    if not genero_coincide_con_preferencia(perfil, preferencias):
        return 0.0

    score = 0.0

    # Partimos de 1 punto por coincidir en género
    score += 1.0

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

    return score


# ===============================
# Perfiles sugeridos (feed)
# ===============================

def obtener_perfiles_sugeridos(
    perfil_usuario: Perfil,
    preferencias: Preference,
    limite: int = 30,
    con_score: bool = False,
):
    """
    Devuelve:
      - si con_score == False: lista de Perfiles sugeridos
      - si con_score == True: lista de tuplas (Perfil, score)

    Importante:
      * género se respeta SIEMPRE, incluso en el camino "suave" (score >= 1).
    """
    otros = obtener_otros_perfiles(perfil_usuario)

    compatibles = []

    for p in otros:
        # primero vemos si cumple los filtros duros (incluye género)
        hard_ok = perfil_cumple_preferencias(p, preferencias)
        score = calcular_score(preferencias, p)

        if hard_ok:
            compatibles.append((p, score))
        else:
            # si no cumple todos, igual calculamos score
            # pero OJO: calcular_score ya devuelve 0 si el género no coincide
            if score >= 1:
                compatibles.append((p, score))

    # ordenar por score desc
    compatibles.sort(key=lambda x: x[1], reverse=True)

    if con_score:
        # devolvemos tuplas (perfil, score)
        return compatibles[:limite]

    # si no, solo los perfiles
    perfiles_ordenados = [p for p, _ in compatibles]
    return perfiles_ordenados[:limite]
