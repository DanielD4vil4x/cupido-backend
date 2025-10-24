from django.urls import path
from . import views

app_name = "auth"

urlpatterns = [
    # Registro y verificación
    path("register/", views.RegisterView.as_view(), name="register"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("resend-code/", views.ResendVerificationCodeView.as_view(), name="resend_code"),

    # Login y logout
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("logout-all/", views.LogoutAllView.as_view(), name="logout_all"),

    # Recuperación de contraseña
    path("password-reset/request/", views.PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset/confirm/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # Cambiar y desactivar cuenta
    path("password/change/", views.PasswordChangeView.as_view(), name="password_change"),
    path("deactivate/", views.DeactivateAccountView.as_view(), name="deactivate"),

    # Sesión actual
    path("session/", views.SessionInfoView.as_view(), name="session_info"),
]



