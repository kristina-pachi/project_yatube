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


@cache_page(20)
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    template = 'posts/profile.html'
    all_posts = author.posts.all()
    paginator = Paginator(all_posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count = len(all_posts)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=user, author=author).exists()
    else:
        following = False
    context = {
        'author': author,
        'user': user,
        'page_obj': page_obj,
        'count': count,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    one_post = get_object_or_404(Post, id=post_id)
    comments = one_post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'one_post': one_post,
        'post_id': post_id,
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
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/follow.html'
    title = 'Посты ваших любимых авторов'
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@authorized_only
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    following = Follow.objects.filter(user=user, author=author)
    if author != user and not following.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=username)


@authorized_only
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    following = Follow.objects.filter(user=request.user, author=author)
    if following.exists():
        following.delete()
    return redirect('posts:profile', username=username)
