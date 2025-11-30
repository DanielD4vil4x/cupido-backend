from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base



# CONFIG POSTGRES

DATABASE_URL = "postgresql+psycopg2://root:iazfqaey4gzsqeij@190.90.114.214:5433/cupid"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# MODELO PERFIL

class Perfil(Base):
    __tablename__ = "perfil"

    perfil_id = Column(Integer, primary_key=True)
    hobbies = Column(String)
    estatura = Column(Integer)
    estado = Column(String)
    likes = Column(Integer)
    fecharegistro = Column(String)
    preferencias_id = Column(Integer)
    programa_academico_id = Column(Integer)
    ubicacion_id = Column(Integer)
    usuario_id = Column(Integer)

class Preference(Base):
    __tablename__ = "preferences_app_preference"

    id = Column(Integer, primary_key=True)

    rango_edad_min = Column(Integer)
    rango_edad_max = Column(Integer)
    rango_estatura_min = Column(Integer)
    rango_estatura_max = Column(Integer)
    ubicacion = Column(String(100))
    genero_preferido = Column(String(50))
    hobbies_preferidos = Column(String) 
    fecha_creacion = Column(String)     

    


#  FUNCIÓN 

def obtener_perfil(user_id: int):
    db = SessionLocal()
    try:
        perfil = db.query(Perfil).filter(Perfil.usuario_id == user_id).first()
        return perfil
    finally:
        db.close()

def obtener_preferencias_por_perfil(perfil: Perfil):
    db = SessionLocal()
    try:
        if perfil.preferencias_id is None:
            return None

        preferencias = (
            db.query(Preference)
            .filter(Preference.id == perfil.preferencias_id)
            .first()
        )
        return preferencias
    finally:
        db.close()

def normalizar_hobbies(cadena: str) -> set[str]:
    if not cadena:
        return set()
    return {h.strip().lower() for h in cadena.split(",") if h.strip()}

def perfil_cumple_preferencias(perfil: Perfil, preferencias: Preference) -> bool:
    
    if preferencias.rango_estatura_min is not None and perfil.estatura is not None:
        if perfil.estatura < preferencias.rango_estatura_min:
            return False

    if preferencias.rango_estatura_max is not None and perfil.estatura is not None:
        if perfil.estatura > preferencias.rango_estatura_max:
            return False

    pref_hobbies = normalizar_hobbies(preferencias.hobbies_preferidos)
    perfil_hobbies = normalizar_hobbies(perfil.hobbies)

    if pref_hobbies:
        if not (pref_hobbies & perfil_hobbies):
            return False

    # 3) Filtro por ubicación (aquí depende de cómo resuelvas ubicacion_id)
    # Si tienes una tabla Ubicacion, normalmente harías un join o una consulta extra.
    # Si no, puedes de momento omitir o adaptarlo si ya tienes el nombre en Perfil.
    # Ejemplo hipotético si tu Perfil tuviera 'ubicacion' como String:
    #
    # if preferencias.ubicacion and perfil.ubicacion:
    #     if preferencias.ubicacion.lower() != perfil.ubicacion.lower():
    #         return False

    # 4) Filtro por genero / edad -> depende de dónde tengas esos datos
    # (usuario, persona, etc.). Lo dejo como idea:
    #
    # if preferencias.genero_preferido and perfil.genero:
    #     if perfil.genero != preferencias.genero_preferido:
    #         return False
    
    # if preferencias.rango_edad_min and perfil.edad:
    #     if perfil.edad < preferencias.rango_edad_min:
    #         return False
    
    # if preferencias.rango_edad_max and perfil.edad:
    #     if perfil.edad > preferencias.rango_edad_max:
    #         return False

    return True


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
    # if preferencias.rango_edad_max is not None and perfil.edad is not None:
    #     if perfil.edad <= preferencias.rango_edad_max:
    #         if preferencias.rango_edad_min is not None and perfil.edad is not None:
    #             if perfil.edad >= preferencias.rango_edad_min:
    #                 score += 1
    
    
    # genero y sus 39 tipos de gey
    # if preferencias.genero_preferido and perfil.genero:
    #     if perfil.genero == preferencias.genero_preferido:
    #         score += 1

        
    return score

def obtener_perfiles_sugeridos(perfil_usuario: Perfil, preferencias: Preference, limite: int = 30):
    db = SessionLocal()
    try:
        # traer perfiles
        otros = (
            db.query(Perfil)
            .filter(Perfil.usuario_id != perfil_usuario.usuario_id)
            .all()
        )

        compatibles = []

        for p in otros:
            if perfil_cumple_preferencias(p, preferencias):
                score = calcular_score(preferencias, p)
                compatibles.append((p, score))
            else:
                score = calcular_score(preferencias, p)
                if score >= 1:
                    compatibles.append((p, score))
            

        # ordernar
        compatibles.sort(key=lambda x: x[1], reverse=True)

        # 3) Devolver solo los perfiles 
        perfiles_ordenados = [p for p, _ in compatibles]
        return perfiles_ordenados[:limite]
    finally:
        db.close()









# user_id = 2

# perfil = obtener_perfil(user_id)
# preferencias = obtener_preferencias_por_perfil(perfil)

# perfil = obtener_perfil(user_id)
# preferencias = obtener_preferencias_por_perfil(perfil)
# perfiles_sugeridos = obtener_perfiles_sugeridos(perfil, preferencias, limite=30)

