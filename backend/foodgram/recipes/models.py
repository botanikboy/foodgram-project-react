from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.utils.text import slugify

from recipes.utils import transliterate

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=250, verbose_name='Название')
    measurement_unit = models.CharField(max_length=10,
                                        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        null=False, blank=False,
        max_length=250, verbose_name='Название',
        unique=True)
    color = models.CharField(
        null=False, blank=False,
        default='#ffffff',
        max_length=7, verbose_name='Цвет в HEX',
        validators=[RegexValidator(
            message='Неверный формат цвета HEX #ffffff',
            regex='^#(?:[0-9a-fA-F]{3}){1,2}$',
            code='invalid_color_format'
        )]
        )
    slug = models.SlugField(
        unique=True, editable=False)

    def save(self, *args, **kwards):
        self.slug = slugify(transliterate(self.name))
        self.color = self.color.upper()
        super(Tag, self).save(*args, **kwards)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return str(self.name)


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор')
    name = models.CharField(
        max_length=250,
        null=False,
        blank=False,
        verbose_name='Название',
        validators=[RegexValidator(
            inverse_match=True,
            message='В названии необходимо использовать буквы.',
            regex='^[0-9\\W]+$',
            code='invalid_name'
        )]
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=False,
        blank=False,
        verbose_name='Картинка')
    text = models.TextField(
        null=False,
        blank=False,
        verbose_name='Текстовое описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='Время приготовления в минутах',
        validators=[
            MinValueValidator(limit_value=1,
                              message='Должно быть больше 1'),
            MaxValueValidator(limit_value=14400,
                              message='Не больше 10 дней'),
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='amounts',)
    amount = models.PositiveSmallIntegerField(
        blank=False, null=False,
        verbose_name='Количество',
        validators=[
            MinValueValidator(limit_value=1,
                              message='Должно быть больше 1'),
            MaxValueValidator(limit_value=32767,
                              message='Не больше 10 дней'),
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredient'),
        ]

    def __str__(self):
        return str(self.id)
