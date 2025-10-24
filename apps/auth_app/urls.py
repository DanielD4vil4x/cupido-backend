# apps/auth_app/urls.py
from django.urls import path

from apps.auth_app.views.register_view import RegisterView
from apps.auth_app.views.verify_view import VerifyEmailView
from apps.auth_app.views.resend_view import ResendVerificationCodeView

# las demás vistas (login, logout, etc.) se importarán cuando existan

app_name = "auth"

urlpatterns = [
    # Registro y verificación
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("resend-code/", ResendVerificationCodeView.as_view(), name="resend_code"),
]
