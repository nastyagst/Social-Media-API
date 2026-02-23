from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserRegistrationView, ProfileRetrieveUpdateView, UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")
urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/profile/", ProfileRetrieveUpdateView.as_view(), name="my_profile"),
    path("", include(router.urls)),
]
