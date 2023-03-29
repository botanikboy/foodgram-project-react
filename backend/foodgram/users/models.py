from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    favorites = models.ManyToManyField(
        'recipes.Recipe', verbose_name='Избранное',
        related_name='favorited', blank=True)
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe', verbose_name='Список покупок', blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name', 'last_name', 'username']


admins, created = Group.objects.get_or_create(name='Administrators')
# admins.permissions.set([Permission.objects.get(name='')])
