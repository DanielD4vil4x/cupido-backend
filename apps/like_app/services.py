# apps/like_app/services.py

from django.db import transaction
from django.db import IntegrityError  # ¡IMPORTANTE! Importar IntegrityError desde django.db
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

    # --- 2. Lógica de Interacción y Match ---
    try:
        with transaction.atomic():
            es_match = False
            
            if accion == 'LIKE':
                # a) Verificar Match Recíproco (B -> A)
                like_reciproco = DetallesLike.objects.filter(
                    usuarioEmisor_id=receptor_id,
                    usuarioReceptor_id=emisor_id,
                    estado='LIKE'
                ).first()

                if like_reciproco:
                    es_match = True
                    
                    # b) Actualizar Like Recíproco y Crear Match
                    like_reciproco.esMutuo = True
                    like_reciproco.save()
                    
                    usuario_a = min(emisor_id, receptor_id)
                    usuario_b = max(emisor_id, receptor_id)
                    
                    Match.objects.create(
                        usuarioA_id=usuario_a,
                        usuarioB_id=usuario_b,
                    )
            
            # c) Crear la nueva interacción (A -> B)
            DetallesLike.objects.create(
                usuarioEmisor_id=emisor_id,
                usuarioReceptor_id=receptor_id,
                estado=accion,
                esMutuo=es_match
            )
            
            # --- 3. Devolver Resultado de la Lógica ---
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

    except IntegrityError:  # ¡CORREGIDO! Usar IntegrityError directamente
        # Manejo de la violación UNIQUE (interacción duplicada)
        raise ValidationError({"message": "Ya has interactuado con este perfil."})
    
    except Exception as e:
        # Errores internos de la DB
        raise Exception(f"Error interno del servicio: {str(e)}")