from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    favorites = models.ManyToManyField(
        'recipes.Recipe', verbose_name='Избранное',
        related_name='favorited', blank=True)
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe', verbose_name='Список покупок', blank=True,
        related_name='shopped')
    email = models.EmailField(unique=True, blank=False, max_length=254)
    first_name = models.CharField(blank=False, max_length=150,
                                  verbose_name='first name')
    last_name = models.CharField(blank=False, max_length=150,
                                 verbose_name='last name')
    password = models.CharField(blank=False, max_length=150,
                                verbose_name='password')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subsribers',
                                   on_delete=models.CASCADE,
                                   verbose_name='Подписчик')
    author = models.ForeignKey(User, related_name='favorite_authors',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')

    def clean(self):
        if self.subscriber == self.author:
            raise ValidationError('Автор и подписчик не могут совпадать')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['subscriber', 'author'],
                                    name='unique_subscription'),
        ]

    def __str__(self):
        return (f'Подписчик: {self.subscriber.username}, '
                f'Автор: {self.author.username}')
