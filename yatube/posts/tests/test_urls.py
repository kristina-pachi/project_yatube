from http import HTTPStatus

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Quotes',
            slug='of-great-men',
            description='цитаты из фильмов и сериалов',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=(
                '— А правда, что вырученные деньги пойдут на помощь детям? '
                '— Да мы все чьи-то дети…'
            )
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
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
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_for_guest_client(self):
        """Статус страниц неавторизованного пользователя."""
        list_urls = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): HTTPStatus.OK,
            reverse('posts:post_detail',
                    args=[self.post.pk]): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            reverse('posts:post_edit',
                    args=[self.post.pk]): HTTPStatus.FOUND,
            '/wild_west/': HTTPStatus.NOT_FOUND
        }

        for address, status in list_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_redirect_url_for_guest_client(self):
        """Редирект для неавторизованного пользователя"""
        list_redirect_urls = {
            reverse('posts:post_create'): reverse('users:login'),
            reverse(
                'posts:post_edit',
                args=[self.post.pk]
            ): reverse('posts:post_detail', args=[self.post.pk]),
        }
        for address, redirect_url in list_redirect_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_url_for_authorized_client(self):
        """Статус страниц авторизованного пользователя."""
        list_urls = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): HTTPStatus.OK,
            reverse('posts:post_detail',
                    args=[self.post.pk]): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse('posts:post_edit',
                    args=[self.post.pk]): HTTPStatus.OK,
            '/wild_west/': HTTPStatus.NOT_FOUND
        }

        for address, status in list_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)
