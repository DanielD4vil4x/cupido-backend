# apps/profile_app/profile/urls.py
from django.urls import path
from profile.views.create_profile_view import CreateView

urlpatterns = [
      path("create-profile/", CreateView.as_view(), name="login"),
]

