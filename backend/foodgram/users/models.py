from django.contrib.auth.models import AbstractUser
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
    password = models.CharField(max_length=150, verbose_name='password')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name', 'last_name', 'username']
