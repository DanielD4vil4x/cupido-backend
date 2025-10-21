from django.urls import path
from apps.auth_app.views.views import home_view


urlpatterns = [
    path('', home_view),
]

