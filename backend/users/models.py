from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.expressions import F
from django.db.models.query_utils import Q


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Электронная почта'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    def clean(self):
        if self.subscriber == self.author:
            raise ValidationError('Нельзя подписываться на себя')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'subscriber'),
                name='unique_subscription'),
            models.CheckConstraint(
                check=~Q(subscriber=F('author')),
                name='dont_subscribe_to_yourself'))
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber} --> {self.author}'
