"""
Módulo de vistas del sistema de autenticación (auth_app).
Agrupa las vistas relacionadas con registro, login, logout,
verificación de correo, recuperación y gestión de contraseñas,
desactivación de cuenta y consulta de sesión.
"""

from .auth import LoginView, RegisterView
from .verification import EmailVerificationView

__all__ = ["LoginView", "RegisterView", "EmailVerificationView"]