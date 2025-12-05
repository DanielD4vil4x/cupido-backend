# apps/like_app/services.py

from django.db import transaction
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from apps.like_app.models import DetallesLike
from apps.match_app.models import Match
from rest_framework.exceptions import ValidationError

User = get_user_model()

def process_user_interaction(emisor_id, receptor_id, accion):
    
    # Asegurar que los IDs son enteros (receptor_id puede venir como string del JSON)
    emisor_id = int(emisor_id)
    receptor_id = int(receptor_id)
    
    # --- 1. Validación del Receptor ---
    if emisor_id == receptor_id:
        raise ValidationError({"message": "No puedes interactuar contigo mismo."})
    
    try:
        # Verificar que el receptor exista
        User.objects.get(usuario_id=receptor_id) 
    except User.DoesNotExist:
         raise ValidationError({"message": "Perfil receptor no encontrado."})

    # --- 2. Verificar si ya existe interacción previa ---
    interaccion_existente = DetallesLike.objects.filter(
        usuarioEmisor_id=emisor_id,
        usuarioReceptor_id=receptor_id
    ).first()
    
    if interaccion_existente:
        # Ya hay una interacción previa, verificar el estado
        if interaccion_existente.esMutuo:
            # Ya hay un match mutuo
            raise ValidationError({"message": "Ya tienes un match con este usuario."})
        
        # Si ya dio LIKE antes, no permitir repetir
        if interaccion_existente.estado == accion:
            raise ValidationError({"message": "Ya has interactuado con este perfil."})
        
        # Si cambió de opinión (ej: DISLIKE -> LIKE), actualizar
        # Esto NO debería generar match porque el otro usuario ya fue rechazado antes

    # --- 3. Lógica de Interacción y Match ---
    try:
        with transaction.atomic():
            es_match = False
            
            if accion == 'LIKE':
                # a) Verificar Match Recíproco (B -> A con LIKE)
                like_reciproco = DetallesLike.objects.filter(
                    usuarioEmisor_id=receptor_id,
                    usuarioReceptor_id=emisor_id,
                    estado='LIKE'
                ).first()

                if like_reciproco and not like_reciproco.esMutuo:
                    es_match = True
                    
                    # b) Actualizar Like Recíproco
                    like_reciproco.esMutuo = True
                    like_reciproco.save()
                    
                    # c) Crear Match
                    usuario_a = min(emisor_id, receptor_id)
                    usuario_b = max(emisor_id, receptor_id)
                    
                    # Verificar que no exista ya el match
                    match_existente = Match.objects.filter(
                        usuarioA_id=usuario_a,
                        usuarioB_id=usuario_b
                    ).exists()
                    
                    if not match_existente:
                        Match.objects.create(
                            usuarioA_id=usuario_a,
                            usuarioB_id=usuario_b,
                        )
            
            # d) Crear o actualizar la interacción (A -> B)
            if interaccion_existente:
                # Actualizar interacción existente
                interaccion_existente.estado = accion
                interaccion_existente.esMutuo = es_match
                interaccion_existente.save()
            else:
                # Crear nueva interacción
                DetallesLike.objects.create(
                    usuarioEmisor_id=emisor_id,
                    usuarioReceptor_id=receptor_id,
                    estado=accion,
                    esMutuo=es_match
                )
            
            # --- 4. Devolver Resultado de la Lógica ---
            if es_match:
                return {
                    "match_found": True, 
                    "message": "¡Match Mutuo!", 
                    "usuario_match": receptor_id,
                    "status_code": 201
                }
            
            elif accion == 'LIKE':
                return {
                    "match_found": False, 
                    "message": "Like registrado.",
                    "status_code": 201
                }
            
            else: # DISLIKE
                return {
                    "match_found": False, 
                    "message": "Descarte registrado.",
                    "status_code": 201
                }

    except IntegrityError:
        raise ValidationError({"message": "Error al procesar la interacción."})
    
    except Exception as e:
        raise Exception(f"Error interno del servicio: {str(e)}")