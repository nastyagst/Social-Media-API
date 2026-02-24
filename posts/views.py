from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Count
from django.db import IntegrityError
from django.utils.dateparse import parse_datetime

from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly
from .tasks import create_scheduled_post


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["author"]
    search_fields = ["hashtags", "text"]

    def get_queryset(self):
        return (
            Post.objects.select_related("author")
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        scheduled_time = request.data.get("scheduled_time")

        if scheduled_time:
            eta_time = parse_datetime(scheduled_time)

            if timezone.is_naive(eta_time):
                eta_time = timezone.make_aware(eta_time)

            delay_seconds = (eta_time - timezone.now()).total_seconds()

            if delay_seconds > 0:
                create_scheduled_post.apply_async(
                    args=[
                        request.user.id,
                        request.data.get("text"),
                        request.data.get("hashtags", ""),
                    ],
                    countdown=delay_seconds,
                )
                return Response(
                    {
                        "detail": f"Post scheduled to be published in {int(delay_seconds)} seconds."
                    },
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                return Response(
                    {"detail": "Scheduled time must be in the future!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def feed(self, request):
        following_ids = request.user.following.values_list("following_id", flat=True)
        queryset = self.get_queryset().filter(author_id__in=following_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def my_posts(self, request):
        queryset = Post.objects.filter(author=request.user).order_by("-created_at")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def like(self, request, pk=None):
        post = self.get_object()
        try:
            Like.objects.create(user=request.user, post=post)
            return Response({"detail": "Post liked."}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {"detail": "You already liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def unlike(self, request, pk=None):
        post = self.get_object()
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if deleted:
            return Response({"detail": "Post unliked."}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "You have not liked this post."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def liked_posts(self, request):
        queryset = self.get_queryset().filter(likes__user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["post"]

    def get_queryset(self):
        return (
            Comment.objects.select_related("author", "post")
            .all()
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
