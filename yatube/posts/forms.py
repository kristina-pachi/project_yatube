from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_texts = {'text': 'Текст нового поста',
                      'group': 'Выберите группу'}
        fields = ['text', 'group', 'image']


class PostFormEdit(forms.ModelForm):
    class Meta:
        model = Post
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_texts = {'text': 'Текст редактируемого поста',
                      'group': 'Группа, к которой относится пост'}
        fields = ['text', 'group', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
