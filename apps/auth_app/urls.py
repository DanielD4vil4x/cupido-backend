from django.urls import path
from .views import auth, verification

urlpatterns = [
    path("login/", auth.LoginView.as_view(), name="login"),
    path("register/", auth.RegisterView.as_view(), name="register"),
    path("verify-email/", verification.EmailVerificationView.as_view(), name="verify-email"),
]


