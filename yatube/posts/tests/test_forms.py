import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Dr_Cox')
        cls.group = Group.objects.create(
            title='Quotes',
            slug='of-great-men',
            description='цитаты из фильмов и сериалов',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=(
                'Вы так напугали всю клинику, '
                'что на верхнем этаже в родильном отделении '
                'ребёнок уже пять минут '
                'пытается забраться по пуповине обратно!'
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
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
        form_data = {
            'group': self.group.id,
            'text': '— Кстати, я хочу попросить тебя стать крёстным отцом.'
                    '— Я та-а-ак, та-а-ак польщён!'
                    '— А я та-а-ак, та-а-ак наврал!',
            'image': uploaded,
        }

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small.gif'
            ).exists()
        )

    def test_image_error(self):
        """Форма выдаст ошибку если пользователь отправит не изображение"""
        text = (
            b'ddsfsdfsdfsfsd'
        )
        uploaded = SimpleUploadedFile(
            name='aasdas.txt',
            content=text,
            content_type='text/txt'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Интересно, когда ты говоришь,ты себя сам слышишь '
                    'или так просто дрейфуешь по сознанию?',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertFormError(
            response,
            'form',
            'image',
            'Загрузите правильное изображение. Файл, который вы загрузили, '
            'поврежден или не является изображением.'
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        group = Group.objects.create(
            title='Sorry',
            slug='for-my-stupid-mistakes',
            description='No excuse for me'
        )
        form_data = {
            'group': group.id,
            'text': '— А вы знали, что это не ваш сын?'
                    '— Догадался. Когда я познакомился с его матерью, '
                    'она была на восьмом месяце беременности... '
                    'Но были и другие сигналы.',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.pk]),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )
