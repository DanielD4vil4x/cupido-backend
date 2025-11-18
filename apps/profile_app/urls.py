from django.urls import path, include

urlpatterns = [
    path("profileManagement/", include("apps.profile_app.subapps.profile.urls")),
<<<<<<< Updated upstream
    path("", include("apps.profile_app.subapps.imageupload.urls")),
=======
    path("", include("apps.profile_app.subapps.imageUpload.urls")),
>>>>>>> Stashed changes
]
