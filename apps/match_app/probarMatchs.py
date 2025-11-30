# probarMatchs.py
from utils import (
    obtener_perfil,
    obtener_preferencias_por_perfil,
    obtener_perfiles_sugeridos,
)


def mostrar_perfil(perfil):
    print(f"Perfil #{perfil.perfil_id}")
    print(f"  usuario_id: {perfil.usuario_id}")
    print(f"  hobbies   : {perfil.hobbies}")
    print(f"  estatura  : {perfil.estatura}")
    print(f"  estado    : {perfil.estado}")
    print("")


if __name__ == "__main__":
    user_id = 4

    perfil = obtener_perfil(user_id)
    if not perfil:
        print(f"No encontré perfil para usuario_id={user_id}")
        raise SystemExit

    print("PERFIL DEL USUARIO:")
    mostrar_perfil(perfil)

    preferencias = obtener_preferencias_por_perfil(perfil)
    if not preferencias:
        print("Este perfil no tiene preferencias asociadas")
        raise SystemExit

    print("PREFERENCIAS:")
    print(f"  rango_estatura_min: {preferencias.rango_estatura_min}")
    print(f"  rango_estatura_max: {preferencias.rango_estatura_max}")
    print(f"  hobbies_preferidos: {preferencias.hobbies_preferidos}")
    print("")

    print("PERFILES SUGERIDOS:")
    sugeridos = obtener_perfiles_sugeridos(perfil, preferencias, limite=10)

    if not sugeridos:
        print("No se encontraron perfiles compatibles")
    else:
        for p in sugeridos:
            mostrar_perfil(p)
