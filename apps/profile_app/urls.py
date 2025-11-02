from django.urls import path, include

urlpatterns = [
    path("/profileManagement/", include("apps.profile_app.subapps.profile.urls")),
    #path("imageUpload/", include("apps.profile_app.subapps.imageupload.urls")),
]
