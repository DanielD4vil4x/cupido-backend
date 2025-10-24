# apps/auth_app/utils/email_utils.py
"""
Utilidades centralizadas para envío de correos electrónicos.
Incluye:
 - Envío de código de verificación
 - Envío de correos de restablecimiento de contraseña
Con conexión SMTP explícita (TLS) y logs detallados.
"""

import logging
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings

logger = logging.getLogger(__name__)


def send_email(subject: str, to_email: str, text_content: str, html_content: str | None = None) -> bool:
    """
    Envía un correo genérico a través de SMTP.
    Usa get_connection() para forzar conexión TLS explícita (Gmail-friendly).
    """
    from_email = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL
    if not from_email:
        logger.error("EMAIL_HOST_USER no está configurado en settings.")
        return False

    try:
        logger.info(f"Creando conexión SMTP con {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        connection = get_connection(
            backend=settings.EMAIL_BACKEND,
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
            fail_silently=False,
        )

        logger.info(f"Preparando mensaje para {to_email}")
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email],
            connection=connection,
            headers={"Reply-To": settings.DEFAULT_FROM_EMAIL},
        )
        if html_content:
            msg.attach_alternative(html_content, "text/html")
            logger.info("Contenido HTML adjuntado correctamente")

        logger.info("Enviando correo...")
        msg.send(fail_silently=False)
        logger.info(f"Correo enviado correctamente a {to_email}")
        return True

    except Exception as e:
        logger.error(f"Error al enviar correo a {to_email}: {e}")
        return False



# --------------------------------------------------------
# Correos específicos (reutilizan send_email)
# --------------------------------------------------------

def send_verification_email(to_email: str, code: str) -> bool:
    """
    Envía el correo de verificación de registro con el código de validación.
    """
    logger.info(f"Enviando correo de verificación a {to_email} con código {code}")
    subject = "Verifica tu cuenta - cUPido"
    text_content = (
        f"Hola 👋,\n\n"
        f"Tu código de verificación es: {code}\n"
        f"Este código es válido por 10 minutos.\n\n"
        f"Si no solicitaste este código, puedes ignorar este mensaje.\n\n"
        f"Atentamente,\nEl equipo de cUPido ❤️"
    )

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color:#e91e63;">¡Bienvenido a cUPido!</h2>
            <p>Tu código de verificación es:</p>
            <h1 style="color:#e91e63;">{code}</h1>
            <p>Este código es válido por <strong>10 minutos</strong>.</p>
            <p>Si no solicitaste este registro, simplemente ignora este mensaje.</p>
            <br>
            <p>❤️ Equipo cUPido</p>
        </body>
    </html>
    """

    result = send_email(subject, to_email, text_content, html_content)
    logger.info(f"Resultado del envío de correo: {result}")
    return result


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """
    Envía un correo de restablecimiento de contraseña.
    """
    subject = "Restablece tu contraseña - cUPido"
    text_content = (
        f"Hola 👋,\n\n"
        f"Has solicitado restablecer tu contraseña.\n"
        f"Usa el siguiente enlace para continuar:\n{reset_link}\n\n"
        f"Si no solicitaste este cambio, ignora este correo.\n\n"
        f"Equipo cUPido ❤️"
    )

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Restablecimiento de contraseña</h2>
            <p>Has solicitado restablecer tu contraseña.</p>
            <p>Haz clic en el siguiente enlace para continuar:</p>
            <a href="{reset_link}" style="color:#e91e63;">Restablecer contraseña</a>
            <br><br>
            <p>Si no solicitaste este cambio, ignora este correo.</p>
            <p>❤️ Equipo cUPido</p>
        </body>
    </html>
    """

    return send_email(subject, to_email, text_content, html_content)
