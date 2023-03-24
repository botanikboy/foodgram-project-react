from django.contrib import admin
from recipes.models import Ingredient, Recipe, Tag, Subscription


class RecipeAdmin(admin.ModelAdmin):
    feilds = ['name', 'author']
admin.site.register([Ingredient, Tag, Subscription])
admin.site.register(Recipe, RecipeAdmin)
