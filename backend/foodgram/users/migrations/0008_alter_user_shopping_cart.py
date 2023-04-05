# Generated by Django 3.2 on 2023-04-04 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_rename_inrgedientamount_ingredientamount'),
        ('users', '0007_rename_shoping_cart_user_shopping_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='shopping_cart',
            field=models.ManyToManyField(blank=True, related_name='shopped', to='recipes.Recipe', verbose_name='Список покупок'),
        ),
    ]