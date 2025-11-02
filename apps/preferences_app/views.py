# apps/preferences_app/views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Preference, Filter
from .serializers import PreferenceSerializer, FilterSerializer

class PreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = PreferenceSerializer
    permission_classes = [AllowAny]
    queryset = Preference.objects.all()

class FilterViewSet(viewsets.ModelViewSet):
    queryset = Filter.objects.all()
    serializer_class = FilterSerializer

    def get_queryset(self):
        queryset = Filter.objects.all()
        usuario_id = self.request.query_params.get('usuario', None)
        if usuario_id is not None:
            queryset = queryset.filter(usuario_id=usuario_id)
        return queryset