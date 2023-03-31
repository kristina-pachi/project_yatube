import shutil
import tempfile

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django import forms

from ..models import Group, Post, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Eric')
        cls.user_2 = User.objects.create_user(username='Я')
        cls.group = Group.objects.create(
            title='Quotes',
            slug='of-great-men',
            description='цитаты из фильмов и сериалов',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=(
                'СПИД был популярен в 80-е — 90-е годы, '
                'сейчас все тащатся от рака!'
            ),
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            text='Мой любимый персонаж!',
            post=cls.post,
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=[self.post.pk]): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    args=[self.post.pk]): 'posts/create_post.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_fields_post(self, response):
        """Проверка полей"""
        for number in range(Post.objects.count()):
            post = response.context['page_obj'][number]
            self.assertEqual(post.author.username, f'{self.user}')
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.group.title, f'{self.group}')
            self.assertEqual(post.image, self.post.image)
            self.assertEqual(
                post, Post.objects.get(pk=Post.objects.count() - number)
            )

    def test_cache_index(self):
        """Кеширование главной страницы"""
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.content
        Post.objects.create(
            author=self.user,
            group=self.group,
            text=(
                'Если ты окончательно потерял чувство юмора, '
                'ты всегда можешь устроиться сценаристом в сериал «Друзья».'
            )
        )
        response = self.authorized_client.get(reverse('posts:index'))
        new_post = response.content
        self.assertEqual(new_post, post)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        new_new_post = response.content
        self.assertNotEqual(new_new_post, new_post)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_fields_post(response)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.check_fields_post(response)
        self.assertEqual(response.context['group'], self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.check_fields_post(response)
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.pk])
        )
        self.assertEqual(
            response.context.get('one_post').author.username,
            f'{self.user.username}'
        )
        self.assertEqual(
            response.context.get('one_post').text,
            f'{self.post.text}'
        )
        self.assertEqual(
            response.context.get('one_post').group.title,
            f'{self.group}' or None
        )
        self.assertEqual(
            response.context.get('one_post').image, self.post.image
        )

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_2_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[self.post.pk])
        )
        form_field = response.context.get('form')
        self.assertIsNotNone(form_field)

    def test_post_on_pages(self):
        """Пост добавлен на главной, в группу, в профайл """
        url_list = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        ]
        for url in url_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                posts = response.context['page_obj']
                self.assertIn(self.post, posts)

    def test_post_not_in_group_profile(self):
        user = User.objects.create_user(username='me')
        group = Group.objects.create(
            title='End',
            slug='of-my-fantasy',
            description='...',
        )
        urls = [
            reverse(
                'posts:group_list',
                kwargs={'slug': group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': user.username}
            )
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                context = response.context['page_obj']
                self.assertFalse(self.post in context)

    def test_creat_comment(self):
        """Добавление комментария"""
        posts_count = Comment.objects.count()
        form_data = {
            'text': 'Ля-ля-ля'
        }
        self.guest_client.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(Comment.objects.count(), posts_count + 1)
        self.assertFalse(
            Comment.objects.filter(
                text=form_data["text"]
            ).exists()
        )
        self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), posts_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data["text"]
            ).exists()
        )

    def test_comment_on_page(self):
        """Комментарий добавлен на страницу поста"""
        page = reverse(
            'posts:post_detail', args=[self.post.pk]
        )
        response = self.authorized_client.get(page)
        comments = response.context['comments']
        self.assertIn(self.comment, comments)

    def test_following(self):
        """Авторизованный пользователь может подписаться"""
        page = reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        )
        self.authorized_client_2.get(page)
        self.assertTrue(
            Follow.objects.filter(user=self.user_2, author=self.user).exists()
        )

    def test_unfollowing(self):
        """Авторизованный пользователь может отписаться"""
        Follow.objects.create(user=self.user_2, author=self.user)
        page = reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username}
        )
        self.authorized_client_2.get(page)
        self.assertFalse(
            Follow.objects.filter(user=self.user_2, author=self.user).exists()
        )

    def test_posts_author_on_page(self):
        """Посты автора появляются в ленте"""
        Follow.objects.create(user=self.user_2, author=self.user)
        page = reverse('posts:follow_index')
        response = self.authorized_client_2.get(page)
        posts = response.context['page_obj']
        self.assertIn(self.post, posts)

        response = self.authorized_client.get(page)
        posts = response.context['page_obj']
        self.assertNotIn(self.post, posts)
