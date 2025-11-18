from django.urls import path, include

urlpatterns = [
    path("profileManagement/", include("apps.profile_app.subapps.profile.urls")),
    path("", include("apps.profile_app.subapps.imageUpload.urls")),
]
