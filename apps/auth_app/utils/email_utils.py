"""
Utilidades centralizadas para envío de correos electrónicos con formato estructurado.
Incluye:
 - Envío de código de verificación con plantilla
 - Envío de restablecimiento de contraseña con plantilla
"""

import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

FOOTER_IMAGE = "https://i.postimg.cc/htWQx7q5/logo-Fix.webp"


def build_markdown_email(title: str, body_lines: list[str]) -> str:
    """
    Construye un correo con estilo tipo markdown en texto plano.
    Diseño clásico, con separadores, bloques de información y firma final personalizada.
    """

    header = (
        "============================================\n"
        f"{title}\n"
        "============================================\n"
    )

    body = "\n".join(f"- {line}" for line in body_lines)

    footer = (
        "\n--------------------------------------------\n"
        "Atentamente,\n"
        "Equipo de cUPido\n"
        f"Imagen de referencia: {FOOTER_IMAGE}\n"
        "--------------------------------------------"
    )

    return f"{header}\n{body}\n{footer}"


def send_email(subject: str, to_email: str, text_content: str) -> bool:
    """
    Envía un correo de texto plano usando la configuración SMTP de Django.
    """

    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    if not from_email:
        logger.error("No se ha configurado DEFAULT_FROM_EMAIL ni EMAIL_HOST_USER.")
        return False

    try:
        logger.debug(f"Enviando correo a {to_email} desde {from_email}")
        send_mail(
            subject=subject,
            message=text_content,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        logger.info(f"Correo enviado correctamente a {to_email}")
        return True

    except Exception as e:
        logger.error(f"Error al enviar correo a {to_email}: {e}")
        return False


def send_verification_email(to_email: str, code: str) -> bool:
    subject = "Verificación de cuenta - cUPido"

    content = build_markdown_email(
        "Verificación de cuenta",
        [
            "Se ha generado un código de verificación.",
            f"Código: {code}",
            "Válido por 10 minutos.",
            "Si no solicitó esta verificación, ignore el mensaje.",
        ],
    )

    return send_email(subject, to_email, content)


def send_password_reset_email(to_email: str, token: str) -> bool:
    subject = "Restablecimiento de contraseña - cUPido"

    content = build_markdown_email(
        "Solicitud de restablecimiento de contraseña",
        [
            "Se ha recibido una petición para restablecer la contraseña.",
            f"Token de recuperación: {token}",
            "Válido por 30 minutos.",
            "Si no solicitó este procedimiento, ignore el mensaje.",
        ],
    )

    return send_email(subject, to_email, content)
