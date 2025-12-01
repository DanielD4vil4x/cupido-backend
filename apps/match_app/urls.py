# # apps/match_app/urls.py
# from django.urls import path

# urlpatterns = [
#     # Puedes dejarlo vacío por ahora, pero debe existir
# ]

# apps/match_app/urls.py

from django.urls import path
from .views import MatchRecommendationsView

urlpatterns = [
    path(
        "recommendations/",
        MatchRecommendationsView.as_view(),
        name="match-recommendations",
    ),
]
