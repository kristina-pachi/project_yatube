from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.core.paginator import Paginator

from .models import Post, Group, User, Follow
from .forms import PostForm, PostFormEdit, CommentForm


def authorized_only(func):
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/auth/login/')
    return check_user


def piginator(request, post):
    paginator = Paginator(post, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20)
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related().all()
    return render(request, template, {'page_obj': piginator(request, posts)})


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'page_obj': piginator(request, posts),
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    template = 'posts/profile.html'
    posts = author.posts.all()
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=user, author=author).exists()
    else:
        following = False
    context = {
        'author': author,
        'user': user,
        'page_obj': piginator(request, posts),
        'count': posts.count(),
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    one_post = get_object_or_404(Post, id=post_id)
    comments = one_post.comments.all()
    form = CommentForm()
    context = {
        'one_post': one_post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@authorized_only
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user.username)
        return render(request, 'posts/create_post.html', {'form': form})
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    one_post = get_object_or_404(Post, id=post_id)
    if request.user != one_post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostFormEdit(
        request.POST or None,
        instance=one_post,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True, 'post_id': post_id})


@authorized_only
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@authorized_only
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    template = 'posts/follow.html'
    title = 'Посты ваших любимых авторов'
    context = {
        'title': title,
        'page_obj': piginator(request, posts),
    }
    return render(request, template, context)


@authorized_only
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@authorized_only
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    following = Follow.objects.filter(user=request.user, author=author)
    following.delete()
    return redirect('posts:profile', username=username)
