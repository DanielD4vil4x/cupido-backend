from datetime import date

from rest_framework import serializers

from apps.auth_app.models import Usuario, Genero
from apps.auth_app.utils.validators import calculate_age


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Valida y actualiza los datos básicos de perfil del usuario autenticado.
    Campos actualizables:
    - nombres
    - apellidos
    - genero_id (FK a Genero)
    - fechanacimiento
    - descripcion
    """

    genero_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Usuario
        fields = [
            "nombres",
            "apellidos",
            "genero_id",
            "fechanacimiento",
            "descripcion",
            "estadocuenta",
            "numerotelefono",
        ]
        extra_kwargs = {
            "nombres": {"required": False},
            "apellidos": {"required": False},
            "fechanacimiento": {"required": False},
            "descripcion": {"required": False, "allow_blank": True},
            "estadocuenta": {"required": False}, 
            "numerotelefono": {"required": False},
        }

    def validate_nombres(self, value):
        if value is None or value == "":
            return value
        return value.strip()

    def validate_apellidos(self, value):
        if value is None or value == "":
            return value
        return value.strip()

    def validate_fechanacimiento(self, value: date) -> date:
        if value is None:
            return value
        today = date.today()
        if value >= today:
            raise serializers.ValidationError("La fecha de nacimiento debe ser en el pasado.")
        try:
            age = calculate_age(value)
        except Exception:
            # Fallback mínimo si la util no está disponible
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("Debes tener al menos 18 años.")
        return value

    def validate_genero_id(self, value):
        if value is None:
            return value
        if not Genero.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Género inválido.")
        return value

    def update(self, instance: Usuario, validated_data: dict) -> Usuario:
        # Manejar asignación de genero_id si fue provisto
        genero_id = validated_data.pop("genero_id", None)
        if genero_id is not None:
            instance.genero = Genero.objects.get(pk=genero_id) if genero_id else None

        # Asignar campos simples
        for field in ["nombres", "apellidos", "fechanacimiento", "descripcion", "estadocuenta","numerotelefono"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance


