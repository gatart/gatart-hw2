from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Post, Category, Comment
from .forms import CommentForm, ProfileForm, PostForm
from .utils import select_posts, select_posts_for_author
from .mixins import (
    PostCreateUpdateMixin,
    CommentMixin,
    ProfileMixin,
    PostDeleteUpdateMixin,
)


User = get_user_model()
OBJ_ON_PAGE = 10


class ProfileDetailView(ProfileMixin, ListView):
    template_name = 'blog/profile.html'
    paginate_by = OBJ_ON_PAGE

    def get_queryset(self):
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        if self.profile != self.request.user:
            return select_posts(author=self.profile).order_by('-pub_date')

        return select_posts_for_author().filter(
            author=self.profile
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['user'] = self.request.user
        return context


class ProfileUpdateView(ProfileMixin, LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = ProfileForm
    user = None

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(
            User,
            username=self.kwargs['username'],
        )
        if self.user != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.user.get_username()}
        )


class PostCreateView(PostCreateUpdateMixin, CreateView):

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = OBJ_ON_PAGE

    def get_queryset(self):
        return select_posts().order_by('-pub_date')


class PostUpdateView(PostDeleteUpdateMixin, PostCreateUpdateMixin, UpdateView):
    pk_field = 'post_id'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostDeleteUpdateMixin, LoginRequiredMixin, DeleteView):
    model = Post
    pk_field = 'post_id'
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:index')


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    form_class = PostForm
    template_name = 'blog/detail.html'

    def get_object(self, **kwargs):
        post_data = get_object_or_404(
            select_posts_for_author(),
            pk=self.kwargs['post_id'],
        )
        if (post_data.author != self.request.user
                and not (post_data.is_published
                         and post_data.category.is_published
                         and post_data.pub_date <= timezone.now())):
            raise Http404

        return post_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryDetailView(ListView):
    model = Category
    template_name = 'blog/category.html'
    slug_field = 'category_slug'
    slug_url_kwarg = 'category_slug'
    paginate_by = OBJ_ON_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )

        return select_posts(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin,
                        CommentMixin,
                        CreateView
                        ):
    blog_post = None
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.blog_post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.blog_post
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    model = Comment
    pk_field = 'comment_id'
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['post_id'])
        if self.get_object().author != request.user:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(LoginRequiredMixin,
                        CommentMixin,
                        UpdateView,
                        ):
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_object(self, **kwargs):
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            author=self.request.user
        )

    def dispatch(self, request, *args, **kwargs):
        old_shit = super().dispatch(request, *args, **kwargs)
        self.blog_post = get_object_or_404(
            select_posts(),
            pk=kwargs['post_id']
        )
        return old_shit
