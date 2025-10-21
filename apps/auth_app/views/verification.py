import random
import redis
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

r = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)

class EmailVerificationView(APIView):
    """
    Envía un código de verificación al correo institucional.
    """
    throttle_scope = "verify_email"

    def post(self, request):
        email = request.data.get("email")
        if not email or not email.endswith("@unipamplona.edu.co"):
            return Response({"error": "Correo institucional inválido."},
                            status=status.HTTP_400_BAD_REQUEST)

        code = f"{random.randint(100000, 999999)}"
        r.setex(f"verify:{email}", 600, code)  # TTL de 10 min

        send_mail(
            "Código de verificación - cUPido",
            f"Tu código es: {code} (válido por 10 minutos).",
            "no-reply@cupido.com",
            [email],
        )

        return Response({"message": "Código enviado con éxito."}, status=200)
