# Generated by Django 3.2 on 2023-03-28 05:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_shoping_cart'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='shoping_cart',
            new_name='shopping_cart',
        ),
    ]