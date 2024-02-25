from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse

from .models import Post, Comment
from .forms import PostForm


User = get_user_model()


class PostCreateUpdateMixin(LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.files = self.request.FILES
        return super().form_valid(form)


class PostDeleteUpdateMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class ProfileMixin:
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
