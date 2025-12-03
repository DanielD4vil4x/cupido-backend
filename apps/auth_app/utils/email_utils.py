"""
Utilidades centralizadas para envío de correos electrónicos de texto plano.
Incluye:
 - Envío de código de verificación
 - Envío de restablecimiento de contraseña
"""

import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_email(subject: str, to_email: str, text_content: str) -> bool:
    """
    Envía un correo de texto plano usando la configuración SMTP de Django.
    """
    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    if not from_email:
        logger.error("❌ No se ha configurado DEFAULT_FROM_EMAIL ni EMAIL_HOST_USER.")
        return False

    try:
        logger.debug(f"📤 Enviando correo a {to_email} desde {from_email}")
        send_mail(
            subject=subject,
            message=text_content,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        logger.info(f"✅ Correo enviado correctamente a {to_email}")
        return True

    except Exception as e:
        logger.error(f"❌ Error al enviar correo a {to_email}: {e}")
        return False

def send_verification_email(to_email: str, code: str) -> bool:
    subject = "Verifica tu cuenta - cUPido"
    text_content = (
        f"Hola 👋,\n\n"
        f"Tu código de verificación es: {code}\n"
        f"Este código es válido por 10 minutos.\n\n"
        f"Si no solicitaste este código, puedes ignorar este mensaje.\n\n"
        f"Atentamente,\nEl equipo de cUPido ❤️"
    )
    return send_email(subject, to_email, text_content)
    
def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    subject = "Recupera tu contraseña - cUPido"
    text_content = (
        f"Hola 👋,\n\n"
        f"Recibimos una solicitud para restablecer tu contraseña.\n"
        f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n"
        f"{reset_link}\n\n"
        f"Este enlace es válido por 30 minutos.\n"
        f"Si no solicitaste este cambio, puedes ignorar este mensaje.\n\n"
        f"Atentamente,\nEl equipo de cUPido ❤️"
    )
    return send_email(subject, to_email, text_content)

