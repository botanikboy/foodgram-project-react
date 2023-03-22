from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=250, verbose_name='Название')
    measurement_unit = models.CharField(max_length=10,
                                        verbose_name='Единицы измерения')


class Tag(models.Model):
    name = models.CharField(null=False, blank=False,
                            max_length=250, verbose_name='Название')
    color = models.CharField(null=False, blank=False,
                             verbose_name='Цвет в HEX')
    slug = models.SlugField(null=False, blank=False,
                            unique=True)


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    name = models.CharField(max_length=250, null=False, blank=False,
                            verbose_name='Название')
    image = models.ImageField(null=False, blank=False,
                              verbose_name='Картинка')
    text = models.TextField(null=False, blank=False,
                            verbose_name='Текстовое описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.IntegerField(null=False, blank=False,
                                       verbose_name='Время приготовления')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subsribers',
                                   verbose_name='Подписчик')
    author = models.ForeignKey(User, related_name='favorite_authors',
                               verbose_name='Автор')
