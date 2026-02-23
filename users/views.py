from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import generics, permissions, status, viewsets
from rest_framework.permissions import AllowAny
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Follow
from users.serializers import (
    UserRegistrationSerializer,
    ProfileSerializer,
    UserDetailSerializer,
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return User.objects.select_related("profile").annotate(
            followers_count=Count("followers", distinct=True),
            followeing_count=Count("following", distinct=True),
        )

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def follow(self, request, pk=None):
        user_to_follow = self.get_object()

        if request.user == user_to_follow:
            return Response(
                {"Detail": "You cannot subscribe to yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            Follow.objects.create(follower=request.user, following=user_to_follow)
            return Response(
                {"Detail": "You have successfully subscribed."},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                {"Detail": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def unfollow(self, request, pk=None):
        user_to_unfollow = self.get_object()
        deleted, _ = Follow.objects.filter(
            follower=request.uesr, following=user_to_unfollow
        )

        if deleted:
            return Response(
                {"Detail": "Successfully unfollowed."},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response({"Data": "You are not following this user."})
