from django.urls import path
from .views import home_view  # Asegúrate de tener esta vista

urlpatterns = [
    path('', home_view),
]

