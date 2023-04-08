# Generated by Django 3.2 on 2023-04-08 10:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_ingredientamount_unique_ingredient'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterField(
            model_name='ingredientamount',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1, message='Должно быть больше 1'), django.core.validators.MaxValueValidator(limit_value=32767, message='Не больше 10 дней')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1, message='Должно быть больше 1'), django.core.validators.MaxValueValidator(limit_value=14400, message='Не больше 10 дней')], verbose_name='Время приготовления в минутах'),
        ),
        migrations.DeleteModel(
            name='Subscription',
        ),
    ]
