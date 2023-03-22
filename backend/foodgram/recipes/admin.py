from django.contrib import admin
from recipes.models import Ingredient, Recipe, Tag, Subscription

admin.site.register([Recipe, Ingredient, Tag, Subscription])
