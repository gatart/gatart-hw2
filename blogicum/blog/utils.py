from django.utils import timezone

from .models import Post


def select_posts_for_author():
    return Post.objects.select_related(
        'category',
        'location',
        'author',
    )


def select_posts(**kwargs):
    return select_posts_for_author().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
        **kwargs,
    )
