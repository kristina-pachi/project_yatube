from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Sheldon')
        cls.group = Group.objects.create(
            title='Quotes',
            slug='of-great-men',
            description='цитаты из фильмов и сериалов',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=(
                '— Извините, я опоздал. '
                '— Что случилось? '
                '— Да ничего, я просто не хотел приходить.'
            )
        )

    def test_models_have_correct_object_names(self):
        """Проверка поле __str__ объектов post и group"""
        models_str = {
            self.post: self.post.text[:15],
            self.group: self.group.title
        }

        for field, value in models_str.items():
            with self.subTest(value=value):
                self.assertEqual(value, str(field))
