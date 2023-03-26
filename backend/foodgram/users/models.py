from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    favorites = models.ManyToManyField(
        'recipes.Recipe', verbose_name='Избранное',
        related_name='favorited', blank=True)
    shoping_cart = models.ManyToManyField(
        'recipes.Ingredient', verbose_name='Список покупок', blank=True)


Group.objects.get_or_create(name='Users')
admins, created = Group.objects.get_or_create(name='Administrators')
# admins.permissions.set([Permission.objects.get(name='')])
