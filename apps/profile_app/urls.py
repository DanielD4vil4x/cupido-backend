# apps/profile_app/urls.py
from django.urls import path, include

urlpatterns = [
    path("preferences-filter/", include("apps.profile_app.preferences_filter.urls")),
    path("image-charge/", include("apps.profile_app.image_charge.urls")),
    path("profile/", include("apps.profile_app.profile.urls")),
    // path de get y update por definir para genelaizar uso de informacion en subaplicaciones
]
