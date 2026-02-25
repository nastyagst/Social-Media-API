from rest_framework import serializers

from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.email")

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "text", "created_at")
        read_only_fields = ("created_at",)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.email")
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "text",
            "image",
            "hashtags",
            "created_at",
            "scheduled_time",
            "likes_count",
            "comments_count",
        )
        read_only_fields = ("created_at",)
