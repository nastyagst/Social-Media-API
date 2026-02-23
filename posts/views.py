from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Post
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["author"]
    search_fields = ["hashtags", "text"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def feed(self, request):
        following_ids = request.user.following.values_list("following_id", flat=True)
        queryset = Post.objects.filter(author_id__in=following_ids).order_by(
            "-created_at"
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def my_posts(self, request):
        queryset = Post.objects.filter(author=request.user).order_by("-created_at")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
