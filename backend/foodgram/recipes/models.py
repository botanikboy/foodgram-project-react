from django.contrib.auth import get_user_model
from django.db import models
from django.utils.html import format_html
from django.utils.text import slugify

from recipes.utils import transliterate

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=250, verbose_name='Название')
    measurement_unit = models.CharField(max_length=10,
                                        verbose_name='Единицы измерения')

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Tag(models.Model):
    name = models.CharField(null=False, blank=False,
                            max_length=250, verbose_name='Название',
                            unique=True)
    color = models.CharField(null=False, blank=False,
                             default='#ffffff',
                             max_length=7, verbose_name='Цвет в HEX',
                             )
    slug = models.SlugField(unique=True, editable=False)

    def colored_name(self):
        return format_html(
            '<span style="color: {};">{}</span>',
            self.color,
            self.name,
        )

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwards):
        self.slug = slugify(transliterate(self.name))
        self.color = self.color.upper()
        super(Tag, self).save(*args, **kwards)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    name = models.CharField(max_length=250, null=False, blank=False,
                            verbose_name='Название')
    image = models.ImageField(
        null=True, blank=True,
        verbose_name='Картинка')
    text = models.TextField(null=False, blank=False,
                            verbose_name='Текстовое описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='InrgedientQuantity',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.IntegerField(
        null=False, blank=False, verbose_name='Время приготовления в минутах')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class InrgedientQuantity(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.DecimalField(decimal_places=2,
                                   max_digits=6,
                                   blank=False, null=False,
                                   verbose_name='Количество')

    def __str__(self):
        return str(self.id)


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subsribers',
                                   on_delete=models.CASCADE,
                                   verbose_name='Подписчик')
    author = models.ForeignKey(User, related_name='favorite_authors',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')

    def __str__(self):
        return (f'Подписчик: {self.subscriber.username}, '
                f'Автор: {self.author.username}')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
