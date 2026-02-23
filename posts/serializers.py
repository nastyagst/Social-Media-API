from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.email")

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
        )
        read_only_fields = ("created_at",)
