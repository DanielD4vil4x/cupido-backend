from django.urls import path
from .views import ProfileUpdateView, PerfilDetailView, PerfilAdminUpdateView

urlpatterns = [
    path("update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("<int:pk>/", PerfilDetailView.as_view(), name="profile-detail"),
    path("admin/<int:pk>/", PerfilAdminUpdateView.as_view(), name="profile-admin-update"),

]
