from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreferenceViewSet, FilterViewSet

router = DefaultRouter()
router.register(r'preferences', PreferenceViewSet, basename='preference')
router.register(r'filters', FilterViewSet, basename='filter')

urlpatterns = [
    path('', include(router.urls)),
]
