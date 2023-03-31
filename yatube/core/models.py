from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель"""
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    text = models.TextField()

    class Meta:
        abstract = True
