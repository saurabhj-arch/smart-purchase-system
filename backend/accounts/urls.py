from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register_view, login_view, profile_view, recently_viewed

urlpatterns = [
    path("register/", register_view),
    path("login/", login_view),
    path("profile/", profile_view),
    path("recently-viewed/", recently_viewed),
    path("token/refresh/", TokenRefreshView.as_view()),  # refresh JWT tokens
]