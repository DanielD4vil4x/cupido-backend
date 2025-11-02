# apps/profile_app/profile/urls.py
from django.urls import path
from .views.create_profile_view import CreateProfileView
from .views.get_profile_view import GetProfileView

urlpatterns = [
    path("create-profile/", CreateProfileView.as_view(), name="create_profile"),
    path("get-profile/", GetProfileView.as_view(), name="get_profile"),
]

