from django.urls import path
from .views import UserInteractionView

app_name = "like_app"

urlpatterns = [
    # POST /api/like/interact/
    path('interact/', UserInteractionView.as_view(), name='user_interaction'),
]