# Generated by Django 3.2 on 2023-04-04 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_rename_inrgedientamount_ingredientamount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/', verbose_name='Картинка'),
        ),
    ]
