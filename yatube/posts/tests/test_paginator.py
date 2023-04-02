from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from ..models import Group, Post

User = get_user_model()


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Боря')
        cls.group = Group.objects.create(
            title='Ель-Цынь',
            slug='ex-president',
            description='Искусство запоя',
        )
        list_of_posts = []
        for i in range(13):
            posts = Post(
                author=cls.user,
                group=cls.group,
                text=f'{i}'
            )
            list_of_posts.append(posts)
        cls.post = Post.objects.bulk_create(list_of_posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        page_list = [
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
        for page in page_list:
            response = self.authorized_client.get(page)
            self.assertEqual(
                len(response.context['page_obj']),
                settings.NUMBER_OF_POSTS
            )
            response = self.authorized_client.get(page + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
