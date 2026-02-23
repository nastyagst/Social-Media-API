from celery import shared_task
from django.contrib.auth import get_user_model

from .models import Post

User = get_user_model()


@shared_task()
def create_scheduled_post(author_id, text, hashtags):
    author = User.objects.get(id=author_id)
    Post.objects.create(author=author, text=text, hashtags=hashtags)
    return f"Post created for user {author}"
